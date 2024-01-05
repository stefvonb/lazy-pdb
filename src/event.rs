use crossterm::event::{self, KeyEvent, MouseEvent, Event as CrosstermEvent};
use std::{
    sync::mpsc, 
    thread,
    time::{Duration, Instant}
};
use anyhow::Result;
use xml_rpc::{Server, Fault};
use std::net::{IpAddr, Ipv4Addr, SocketAddr};

use crate::app::Snapshot;

#[derive(Clone, Debug)]
pub enum Event {
    Tick, // Terminal tick
    Key(KeyEvent), // Keyboard event
    Mouse(MouseEvent), // Mouse event
    Resize(u16, u16), // Terminal resize
    SnapshotReceived(Snapshot), // Snapshot received
    StdoutReceived(String), // Stdout received
    StderrReceived(String), // Stderr received
}

#[derive(Debug)]
pub struct EventHandler {
    pub sender: mpsc::Sender<Event>,
    receiver: mpsc::Receiver<Event>,
    #[allow(dead_code)]
    thread: thread::JoinHandle<()>,
}

impl EventHandler {
    pub fn new(tick_rate: u64, receiver_port: u16) -> Self {
        let tick_rate = Duration::from_millis(tick_rate);
        let (sender, receiver) = mpsc::channel();

        let handler = {
            let sender_for_rpc = sender.clone();
            let sender = sender.clone();

            thread::spawn(move || {
                let mut last_tick = Instant::now();

                let mut rpc_server = Server::new();

                let update_snapshot = move |snapshot: Snapshot| -> Result<String, Fault> {
                    let _ = sender_for_rpc.send(Event::SnapshotReceived(snapshot));
                    Ok("ok".to_string())
                };

                rpc_server.register_simple("update_snapshot", update_snapshot);

                let socket = SocketAddr::new(IpAddr::V4(Ipv4Addr::new(127, 0, 0, 1)), receiver_port);
                let bound_server = rpc_server.bind(&socket).expect("Unable to bind RPC server");
        
                loop {
                    let timeout = tick_rate.checked_sub(last_tick.elapsed()).unwrap_or(tick_rate);

                    if event::poll(timeout).expect("Unable to poll for event") {
                        match event::read().expect("Unable to read event") {
                            CrosstermEvent::Key(e) => {
                                if e.kind == event::KeyEventKind::Press {
                                    sender.send(Event::Key(e))
                                } else {
                                    Ok(())
                                }
                            }
                            CrosstermEvent::Mouse(e) => {
                                sender.send(Event::Mouse(e))
                            }
                            CrosstermEvent::Resize(w, h) => {
                                sender.send(Event::Resize(w, h))
                            }
                            CrosstermEvent::FocusLost => { Ok(()) }
                            CrosstermEvent::FocusGained => { Ok(()) }
                            _ => unimplemented!(),
                        }.expect("Unable to send event")
                    }

                    if last_tick.elapsed() >= tick_rate {
                        sender.send(Event::Tick).expect("Unable to send tick event");
                        last_tick = Instant::now();
                    }

                    bound_server.poll();
                }
            })
        };
        
        Self {
            sender,
            receiver,
            thread: handler,
        }
    }

    pub fn next(&self) -> Result<Event> {
        Ok(self.receiver.recv()?)
    }
}
