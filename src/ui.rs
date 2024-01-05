use ratatui::{
    prelude::{Alignment, Constraint, Direction, Frame, Layout},
    style::{Color, Style},
    widgets::{Block, Borders, Paragraph},
    text::{Line, Span, Text},
};
use std::fs::read_to_string;

use crate::app::{App, AppState, SelectedPanel};

fn get_panel_contents<'a>(app: &'a App, this_panel: SelectedPanel) -> Vec<Line> {
    match this_panel {
        SelectedPanel::CallStack => {
            let mut lines: Vec<Line> = vec![];
            if app.snapshot.stack.is_empty() {
                lines = vec![Line::from("".to_string())];
            } else {
                for (i, frame) in app.snapshot.stack.iter().enumerate() {
                    lines.push(Line::from(vec![
                        Span::styled(format!("{:2} ", i + 1), Style::default().fg(Color::DarkGray)),
                        if i == app.selected_frame {
                            Span::styled(format!("{}:{}", frame.function_name, frame.line_number), Style::default().fg(Color::White).bg(Color::Red))
                        } else {
                            Span::styled(format!("{}:{}", frame.function_name, frame.line_number), Style::default())
                        }
                ]));
                }
            }
            lines
        },
        SelectedPanel::Code => {
            let selected_frame = &app.get_selected_frame();
            if Option::is_none(selected_frame) {
                return vec![Line::from("".to_string())];
            }

            let file_name = &selected_frame.unwrap().file_name;
            let file_contents = read_to_string(file_name).unwrap_or_else(|_| "could not read file".to_string());
            let mut file_lines: Vec<Line> = vec![];
            for (i, line) in file_contents.lines().enumerate() {
                    file_lines.push(Line::from(vec![
                    Span::styled(format!("{:4} ", i + 1), Style::default().fg(Color::DarkGray)),
                    if i == selected_frame.unwrap().line_number as usize - 1 {
                        Span::styled(line.to_string(), Style::default().fg(Color::White).bg(Color::Red))
                    } else {
                        Span::styled(line.to_string(), Style::default())
                    }
                ]));
            }
            file_lines
        }
        SelectedPanel::Variables => {
            let mut lines: Vec<Line> = vec![];
            let selected_frame = &app.get_selected_frame();
            if Option::is_none(selected_frame) {
                return vec![Line::from("".to_string())];
            }
            let selected_frame = selected_frame.unwrap();
            for variable in &selected_frame.local_variables {
                lines.push(Line::from(vec![
                    Span::styled(format!("{:?} ", variable.name), Style::default().fg(Color::DarkGray)),
                    Span::styled(format!("{:?}", variable.value), Style::default()),
                ]));
            }
            for variable in &selected_frame.global_variables {
                lines.push(Line::from(vec![
                    Span::styled(format!("{:?} ", variable.name), Style::default().fg(Color::DarkGray)),
                    Span::styled(format!("{:?}", variable.value), Style::default()),
                    Span::styled("(global)", Style::default().fg(Color::DarkGray).add_modifier(ratatui::style::Modifier::ITALIC)),
                ]));
            }
            lines
        },
        SelectedPanel::Output => {
            let mut lines: Vec<Line> = vec![];
            for output_line in &app.output {
                lines.push(Line::from(vec![
                    Span::styled(format!("{:?} ", output_line.output_type), Style::default().fg(Color::DarkGray)),
                    Span::styled(output_line.contents.to_string(), Style::default()),
                ]));
            }
            lines
        }
    }
}

fn panel_widget<'a>(title: &'a str, app: &'a App, this_panel: SelectedPanel, panel_height: u16) -> Paragraph<'a> {
    let mut style = Style::default().fg(Color::Gray);
    if this_panel == app.selected_panel {
        style = Style::default().fg(Color::White).bg(Color::Blue);
    }
    let panel_contents = get_panel_contents(app, this_panel);
    let contents_height = panel_contents.len() as u16;
    let contents_string = Text::from(panel_contents);

    let mut scroll_amount: u16 = 0;
    if contents_height > panel_height {
        scroll_amount = match this_panel {
            SelectedPanel::Code => app.get_selected_frame().map(|frame| frame.line_number as u16).unwrap_or(0) - 1,
            SelectedPanel::CallStack => app.selected_frame as u16,
            _ => 0,
        };

        scroll_amount = scroll_amount.checked_sub(panel_height / 2).unwrap_or(0);
    }
    Paragraph::new(contents_string).block(
        Block::default()
            .borders(Borders::ALL)
            .title(title)
            .title_alignment(Alignment::Center)
            .title_style(style)
            )
            .scroll((scroll_amount, 0))
}

pub fn render(app: &mut App, frame: &mut Frame) {
    let height = frame.size().height;
    let top_panel_height = height / 2;
    let bottom_panel_height = height - top_panel_height - 1;

    let outer_layout = Layout::default()
        .direction(Direction::Vertical)
        .constraints(vec![
            Constraint::Length(top_panel_height),
            Constraint::Length(bottom_panel_height),
            Constraint::Length(1),
        ])
        .split(frame.size());

    let top_panels = Layout::default()
        .direction(Direction::Horizontal)
        .constraints(vec![Constraint::Percentage(30), Constraint::Percentage(70)])
        .split(outer_layout[0]);

    let bottom_panels = Layout::default()
        .direction(Direction::Horizontal)
        .constraints(vec![Constraint::Percentage(30), Constraint::Percentage(70)])
        .split(outer_layout[1]);

    let status_bar = Layout::default()
        .direction(Direction::Horizontal)
        .constraints(vec![
            Constraint::Percentage(80),
            Constraint::Percentage(5),
            Constraint::Percentage(15),
        ])
        .split(outer_layout[2]);

    frame.render_widget(panel_widget("call stack", app, SelectedPanel::CallStack, top_panel_height), top_panels[0]);

    let file_name = app.get_selected_frame().map(|frame| frame.file_name.clone()).unwrap_or("code".to_string());
    frame.render_widget(panel_widget(&file_name, app, SelectedPanel::Code, top_panel_height), top_panels[1]);

    frame.render_widget(panel_widget("variables", app, SelectedPanel::Variables, bottom_panel_height), bottom_panels[0]);

    frame.render_widget(panel_widget("output", app, SelectedPanel::Output, bottom_panel_height), bottom_panels[1]);

    frame.render_widget(
        Paragraph::new("[c]ontinue | [n]ext | [s]tep | to [r]eturn | s[t]op | [q]uit")
            .block(Block::default())
            .alignment(Alignment::Center),
        status_bar[0],
    );

    frame.render_widget(
        Paragraph::new("Status: ")
            .block(Block::default().style(Style::default()))
            .alignment(Alignment::Right),
        status_bar[1],
    );

    frame.render_widget(
        Paragraph::new(match &app.state {
            AppState::Idle => "Idle",
            AppState::RunningCode => "Running code",
            AppState::Breakpoint => "Breakpoint",
            AppState::Error(e) => e,
        })
        .block(
            Block::default().style(Style::default().bg(Color::White).fg(match &app.state {
                AppState::Idle => Color::Black,
                AppState::RunningCode => Color::Green,
                AppState::Breakpoint => Color::Red,
                AppState::Error(_) => Color::Red,
            })),
        )
        .alignment(Alignment::Center),
        status_bar[2],
    );
}
