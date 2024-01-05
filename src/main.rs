/// Application.
pub mod app;

/// Terminal events handler.
pub mod event;

/// Widget renderer.
pub mod ui;

/// Terminal user interface.
pub mod tui;

/// Application updater.
pub mod update;

use std::io::BufRead;

use anyhow::Result;
use app::{App, OutputType, OutputLine};
use event::{Event, EventHandler};
use ratatui::{backend::CrosstermBackend, Terminal};
use tui::Tui;
use update::update;

fn main() -> Result<()> {
    // Create an application.
    let mut app = App::new();

    // Initialize the terminal user interface.
    let backend = CrosstermBackend::new(std::io::stderr());
    let terminal = Terminal::new(backend)?;
    let events = EventHandler::new(250, 8080);
    let mut tui = Tui::new(terminal, events);
    tui.enter()?;

    // Start the Python program
    let args: Vec<String> = std::env::args().collect();
    let python_file_path = args.get(1).expect("Please provide a Python file to debug.");
    let mut python_process = std::process::Command::new("python")
        .args(&["-m", "ldb", python_file_path])
        .env("PYTHONBREAKPOINT", "ldb.set_trace")
        .stdout(std::process::Stdio::piped())
        .stderr(std::process::Stdio::piped())
        .spawn()
        .expect("Unable to start Python process.");

    let stdio_sender = tui.events.sender.clone();
    let stderr_sender = tui.events.sender.clone();

    let stdout = python_process.stdout.take().unwrap();
    let stderr = python_process.stderr.take().unwrap();

    std::thread::spawn(move || {
        let stdout_lines = std::io::BufReader::new(stdout).lines();
        for line in stdout_lines {
            let _ = stdio_sender.send(Event::StdoutReceived(line.unwrap()));
        }
    });

    std::thread::spawn(move || {
        let stderr_lines = std::io::BufReader::new(stderr).lines();
        for line in stderr_lines {
            let _ = stderr_sender.send(Event::StderrReceived(line.unwrap()));
        }
    });


    // Start the main loop.
    while !app.should_quit {
        // Render the user interface.
        tui.draw(&mut app)?;
        // Handle events.
        match tui.events.next()? {
            Event::Key(key_event) => update(&mut app, key_event),
            Event::SnapshotReceived(snapshot) => {
                app.snapshot = snapshot;
                app.state = app::AppState::Breakpoint;
                app.selected_frame = app.snapshot.stack.len() - 1;
            },
            Event::StdoutReceived(stdout) => {app.output.push(OutputLine { output_type: OutputType::Stdout, contents: stdout });},
            Event::StderrReceived(stderr) => {app.output.push(OutputLine { output_type: OutputType::Stderr, contents: stderr });},
            _ => {}
        };
    }

    // Kill the Python process
    python_process.kill()?;

    // Exit the user interface.
    tui.exit()?;
    Ok(())
}
