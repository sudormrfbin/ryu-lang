use ariadne::{ColorGenerator, Label, Report, ReportKind, Source};
use pyo3::prelude::*;

#[pyfunction]
fn report_error(
    source: String,
    start_pos: usize,
    message: String,
    code: usize,
    labels: Vec<(String, (usize, usize))>,
) {
    let mut colors = ColorGenerator::new();

    // Generate & choose some colours for each of our elements
    // let a = colors.next();
    // let b = colors.next();
    // let out = Color::Fixed(81);

    let source_id = "stdin";

    let mut report = Report::build(ReportKind::Error, source_id, start_pos)
        .with_code(format!("E{code:02}"))
        .with_message(message);

    for (label_msg, (start, end)) in labels {
        report = report.with_label(
            Label::new((source_id, start..end))
                .with_message(label_msg)
                .with_color(colors.next()),
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
