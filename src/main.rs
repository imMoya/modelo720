use polars::prelude::*;

fn main() -> Result<(), PolarsError> {
    // Read a csv file
    let df_csv = CsvReadOptions::default()
        .with_infer_schema_length(None)
        .with_has_header(true)
        .with_parse_options(CsvParseOptions::default().with_try_parse_dates(true))
        .try_into_reader_with_file_path(Some("datasets/Portfolio2023.csv".into()))?
        .finish()?;

    println!("{}", df_csv);

    Ok(())
}
