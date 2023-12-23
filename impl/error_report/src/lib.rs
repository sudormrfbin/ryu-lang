use std::collections::HashMap;

use ariadne::{ColorGenerator, Fmt, Label, Report, ReportKind, Source};
use pyo3::prelude::*;

type ColorId = String;

#[derive(FromPyObject)]
enum MessageSpan {
    Text(String),
    Colored(String, ColorId),
}

type Message = Vec<MessageSpan>;

#[pyfunction]
fn report_error(
    source: String,
    start_pos: usize,
    message: Message,
    code: usize,
    labels: Vec<(Message, (usize, usize))>,
) {
    let mut colors = ColorGenerator::new();

    let mut color_map = HashMap::new();

    let mut build_msg = |msg: Message| -> String {
        msg.into_iter()
            .map(|span| match span {
                MessageSpan::Text(t) => t,
                MessageSpan::Colored(text, color_id) => {
                    let color = color_map.entry(color_id).or_insert_with(|| colors.next());
                    format!("{}", text.fg(*color))
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
        .with_message(build_msg(message));

    for (label_msg, (start, end)) in labels {
        report = report.with_label(
            // TODO: Add color_id to label
            Label::new((source_id, start..end)).with_message(build_msg(label_msg)), // .with_color(colors.next()),
        );
    }

    report
        // .with_note(format!(
        //     "Outputs of {} expressions must coerce to the same type",
        //     "match".fg(out)
        // ))
        .finish()
        .print((source_id, Source::from(source)))
        .unwrap();
}

/// A Python module implemented in Rust.
#[pymodule]
fn error_report(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(report_error, m)?)?;
    Ok(())
}
