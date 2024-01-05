use serde::{Deserialize, Serialize};

#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct Variable {
    pub name: String,
    pub value: String,
    pub python_type: String,
}

#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct Frame {
    pub file_name: String,
    pub line_number: u32,
    pub function_name: String,
    pub local_variables: Vec<Variable>,
    pub global_variables: Vec<Variable>,
}

#[derive(Clone, Debug, Serialize, Deserialize, Default)]
pub struct Snapshot {
    pub stack: Vec<Frame>,
}

#[derive(Clone, Debug, Default)]
pub enum AppState {
    #[default]
    Idle,
    RunningCode,
    Breakpoint,
    Error(String),
}

#[derive(Clone, Debug, Default, PartialEq, Eq, Hash, Copy)]
pub enum SelectedPanel {
    #[default]
    CallStack,
    Code,
    Variables,
    Output,
}

#[derive(Debug, Default)]
pub enum OutputType {
    #[default]
    Stdout,
    Stderr,
}

#[derive(Debug, Default)]
pub struct OutputLine {
    pub output_type: OutputType,
    pub contents: String,
}

#[derive(Debug, Default)]
pub struct App {
    pub should_quit: bool,
    pub snapshot: Snapshot,
    pub state: AppState,
    pub selected_panel: SelectedPanel,
    pub selected_frame: usize,
    pub output: Vec<OutputLine>,
}

impl App {
    pub fn new() -> Self {
        Self::default()
    }

    pub fn quit(&mut self) {
        self.should_quit = true;
    }

    pub fn get_selected_frame(&self) -> Option<&Frame> {
        self.snapshot.stack.get(self.selected_frame)
    }
}

