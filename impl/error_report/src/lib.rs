use std::{collections::HashMap, ops::Range};

use ariadne::{ColorGenerator, Fmt, Label, Report, ReportKind, Source};
use pyo3::prelude::*;

type ColorId = String;

#[derive(FromPyObject)]
enum MessageSpan {
    Text(String),
    Colored(String, ColorId),
}

type Message = Vec<MessageSpan>;

type CharSpan = (usize, usize);

#[derive(FromPyObject)]
enum Mark {
    Text(Message, CharSpan),
    Color(ColorId, CharSpan),
    TextAndColor(Message, ColorId, CharSpan),
}

impl Mark {
    pub fn span(&self) -> CharSpan {
        match self {
            Mark::Text(_, span) => *span,
            Mark::Color(_, span) => *span,
            Mark::TextAndColor(_, _, span) => *span,
        }
    }

    pub fn range(&self) -> Range<usize> {
        let span = self.span();
        span.0..span.1
    }

    pub fn text(&self) -> Option<&Message> {
        match self {
            Mark::Text(text, _) => Some(text),
            Mark::TextAndColor(text, _, _) => Some(text),
            Mark::Color(_, _) => None,
        }
    }

    pub fn color_id(&self) -> Option<&ColorId> {
        match self {
            Mark::TextAndColor(_, color_id, _) => Some(color_id),
            Mark::Color(color_id, _) => Some(color_id),
            Mark::Text(_, _) => None,
        }
    }
}

struct ColorStore {
    generator: ColorGenerator,
    map: HashMap<ColorId, ariadne::Color>,
}

impl ColorStore {
    pub fn new() -> Self {
        Self {
            generator: ColorGenerator::new(),
            map: HashMap::new(),
        }
    }

    pub fn get(&mut self, id: &ColorId) -> ariadne::Color {
        if !self.map.contains_key(id) {
            self.map.insert(id.clone(), self.generator.next());
        }
        self.map[id]
    }
}

#[pyfunction]
fn report_error(
    source: String,
    start_pos: usize,
    message: Message,
    code: usize,
    labels: Vec<Mark>,
) {
    let mut color_store = ColorStore::new();

    let build_msg = |msg: &Message, store: &mut ColorStore| -> String {
        msg.iter()
            .map(|span| match span {
                MessageSpan::Text(t) => t.clone(),
                MessageSpan::Colored(text, color_id) => {
                    format!("{}", text.fg(store.get(color_id)))
                }
            })
            .collect()
    };

    // Generate & choose some colours for each of our elements
    // let a = colors.next();
    // let b = colors.next();
    // let out = Color::Fixed(81);

    let source_id = "stdin";

    let mut report = Report::build(ReportKind::Error, source_id, start_pos)
        .with_code(format!("E{code:02}"))
        .with_message(build_msg(&message, &mut color_store));

    for mark in labels {
        let mut label = Label::new((source_id, mark.range()));

        if let Some(msg) = mark.text() {
            label = label.with_message(build_msg(msg, &mut color_store))
        }
        if let Some(color_id) = mark.color_id() {
            label = label.with_color(color_store.get(color_id));
        }

        report.add_label(label);
    }

    eprintln!();
    report
        // .with_note(format!(
        //     "Outputs of {} expressions must coerce to the same type",
        //     "match".fg(out)
        // ))
        .finish()
        .eprint((source_id, Source::from(source)))
        .unwrap();
    eprintln!();
}

/// A Python module implemented in Rust.
#[pymodule]
fn error_report(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(report_error, m)?)?;
    Ok(())
}
