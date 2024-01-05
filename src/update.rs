use crossterm::event::{KeyCode, KeyEvent};
use serde::{Deserialize, Serialize};

use crate::app::{App, SelectedPanel, AppState};

#[derive(Clone, Debug, Serialize, Deserialize)]
struct DebugAction {
    requested_action: String,
    arguments: Vec<String>,
}

#[derive(Clone, Debug, Serialize, Deserialize)]
struct DebugActionResult {
    requested_action: String,
    arguments: Vec<String>,
    status: String,
    message: String,
}

fn send_rpc_request(request_data: DebugAction) -> Result<DebugActionResult, xml_rpc::Fault> {
    let mut client = xml_rpc::Client::new().unwrap();
    let url = xml_rpc::Url::parse("http://127.0.0.1:8081").unwrap();

    let response: Result<_, xml_rpc::Fault> = client
        .call::<&str, &DebugAction, DebugActionResult>(
            &url,
            "interact_with_debugger",
            &request_data,
        )
        .unwrap();

    response
}

pub fn update(app: &mut App, key_event: KeyEvent) {
    let panel_order = [
        SelectedPanel::CallStack,
        SelectedPanel::Code,
        SelectedPanel::Variables,
        SelectedPanel::Output,
    ];

    match key_event.code {
        KeyCode::Esc | KeyCode::Char('q') => app.quit(),
        KeyCode::Char('c') => {
            if send_rpc_request(DebugAction { requested_action: "continue".to_string(), arguments: vec![], }).is_ok() {
                app.state = AppState::RunningCode;
            }
        },
        KeyCode::Char('n') => {
            if send_rpc_request(DebugAction { requested_action: "next".to_string(), arguments: vec![], }).is_ok() {
                app.state = AppState::RunningCode;
            }
        },
        KeyCode::Char('t') => {
            if send_rpc_request(DebugAction { requested_action: "stop".to_string(), arguments: vec![], }).is_ok() {
                app.state = AppState::Idle;
            }
        },
        KeyCode::Tab => {
            let current_panel_index = panel_order
                .iter()
                .position(|&panel| panel == app.selected_panel)
                .unwrap();
            app.selected_panel = panel_order[(current_panel_index + 1) % panel_order.len()];
        },
        KeyCode::BackTab => {
            let current_panel_index = panel_order
                .iter()
                .position(|&panel| panel == app.selected_panel)
                .unwrap();
            app.selected_panel =
                panel_order[(current_panel_index + panel_order.len() - 1) % panel_order.len()];
        },
        KeyCode::Char('j') | KeyCode::Down => {
            match app.selected_panel {
                SelectedPanel::CallStack => {
                    if app.selected_frame < app.snapshot.stack.len() - 1 {
                        app.selected_frame += 1;
                    }
                },
                _ => {}
            }
        },
        KeyCode::Char('k') | KeyCode::Up => {
            match app.selected_panel {
                SelectedPanel::CallStack => {
                    if app.selected_frame > 0 {
                        app.selected_frame -= 1;
                    }
                },
                _ => {}
            }
        },
        _ => {}
    };
}
