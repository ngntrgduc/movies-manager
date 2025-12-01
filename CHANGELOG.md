# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

<!-- Format:
##[] - 

### Added

### Changed

### Fixed

### Removed

 -->

## [[v0.3.0](https://github.com/ngntrgduc/movie-manager/releases/tag/v0.3.0)]

### Added
- Genres formating utility in `utils/format.py`
- Database utility: `utils/db.py`
    - `fetch_scalar` for executing SQL queries that return a single numeric value
    - `fetch_rows` for executing (parameterized) SQL queries and returning rows with column names
- `print_rows` to print rows in a Rich table, faster than `print_df` (import pandas), optional hide specific columns (hide `rating` and `watched_date` when `status` is 'waiting', similar auto hide empty comlumns feature from `print_df`)
- Implemented tuple-based sort keys in `parse_sort_column` to ensure stable and correct sorting with `print_rows`

CLI:
- `--sort` option for sql command with abbreviation
- SQL files prefix and fuzzy matching fallback for `sql` command
- Allow '+' for ascending and '-' for descending sort order in `sql` command
- `--csv` flag for `backup` command, save data to `data/backup.csv` to have safer recovery
- `--note-contains` option for filtering by note substring in `filter` command
- Average rating and genres count for `stats` command
- `-v/--verbose` flag for `stats` command, showing more statistics
- `recent` command to list recently watched movies, with optional limit number, better than using `sql` command to run `recent.sql`
- `latest` command to list recently added movies, with optional limit number, better than using `sql` command to run `latest.sql`
- `search` command for name or note field, more intuitive than `filter` for searching by text
- `optimize` command to optimize database using VACUUM
- File utilities: `utils/file.py`. Contains `get_file_size` and `convert_bytes`, use for `optimize` command
- Add full year filtering for `watched_date` in `filter` command, prevent mismatch input format with `year`

### Changed
- Use genre lists instead of comma-separated strings to reduce redundancy, improve performance
- Rename utils/data.py to utils/streamlit_helpers.py to better reflect Streamlit-specific helpers
- Move `get_connection` from `utils/movie.py` to `utils/db.py`
- Move hard-coded statuses, types, and countries to `utils/constants.py`

CLI:
- Sorting logic in `filter` command, support more columns and flexible ordering
- Switch to fuzzy matching for column names instead of `resolve_choice` in `sql` command to handle similar column initials
- Use SQL files instead of inline queries in the `stats` command, provide more detailed statistics
- `sql` command use `print_rows` instead of `print_df` to display result, remove pandas dependency for faster runtime
- use `-v/--verbose` flag for optional SQL content display for `sql` command
- Refactor `sql` command structure
    - Move some utilities to `utils/sql.py` and `utils/cli.py`
    - Move SQL file matching to `utils/sql.py`, improve matching logic and messages
    - Add `run_sql` to read and run sql file, with support for parameterized queries, improve reusability
- `filter` command use SQL for filtering instead of pandas, use `print_rows` instead of `print_df`, faster speed
- Show `note` comlumn when `note_contains` is given in `filter` command


### Fixed
- Unable to sort column with percent symbol (%) for `sql` command
- Avoid SettingWithCopyWarning by remove `inplace=True` parameters
- Unable to sort watched_date column because of type str compare to float (None value case)
- Genres being displayed when updating without genres updates
- Match both 'comedy' and 'dark comedy' for genre 'com' for `filter` command, using prefix-match intead

### Removed
- `--stats` for `filter` command because rarely used
- `apply_filters` and `print_df` function in `utils/cli.py`, use SQL to filter by `get_filter_query` and `print_rows` instead, faster speed


## [[v0.2.0](https://github.com/ngntrgduc/movie-manager/releases/tag/v0.2.0)]

Moving data to SQLite database.

### Added
- Script to move data from CSV to SQLite: `csv_to_sqlite.py`
- `timing` decorator in `utils/` to benchmark functions speed
- Movie sqlite database and backup

CLI:
- Sorting by `year`
- `delete`, `get`, `update` command
- `sql` command to run SQL script, provide flexibility and customization
- Show last modified of backup file in `restore` command
- Genres fuzzy matching in `filter` command

### Changed
- `load_data` function use index
- Hangle None values in `add_movie` manually instead of using pandas
- Layout of Add page
- Add `Refresh` button for Data and Edit pages
- Rename Add page and Edit page file name for ordering purpose

CLI:
- `add` command use SQL to add movie to the SQLite database
- `stats` command use SQL for faster runtime
- `backup` use sqlite3.backup instead of shutil, restore to `backup.db`
- `restore` from `backup.db` instead of `backup.csv`


## [[v0.1.3](https://github.com/ngntrgduc/movie-manager/releases/tag/v0.1.3)]

### Added
CLI:
- `rating` filtering
- `backup` command, store backup in `data` folder
- `restore` command to restore data from backup

### Changed
- Rename `demo.csv` to `data.csv`, no more manual handling data file when working
- `genres`, `year` field is required in Edit page
- Change repo name from `movies-manager` to `movie-manager`, fix links in CHANGELOG

CLI:
- Hide `note` column, enable show `note` column using `--note` flag

### Fixed
- Prevent printing all movies in the command line when using `filter` command with just flags

## [[v0.1.2](https://github.com/ngntrgduc/movie-manager/releases/tag/v0.1.2)]

CLI improvement.

### Added
- `stats` command and `--stats` flag for `filter` command to print statistics
    - Improved stats output: excluded fields are no longer shown when filtered.
- Allow adding `status` field, with default is `waiting`
- Allow adding `rating` and `watched_date` when status is `completed` or `dropped`

### Changed
- Partial year matching for `watched_date` filter (supports shorthand years like `-w 25`)
- Change explicit wraps in quotation marks to repr representation
- Refactored year and rating input handling to use a reusable `IntRangeOrNone` Click `ParamType` instead of custom validator functions
- Automatically drop empty columns when printing DataFrame, improve readability
- Keep the `note` column instead of removing it
- From `--sort` flag to `--sort` option handling: support `watched_date` sorting
- Use `AbbrevChoice` instead of `prompt_with_choice` function, reduce cognitive load (value_proc, custom Click-based prompt message). Using custome Choice type is more natural when prompting, with default promp message from Click.

## [[v0.1.1](https://github.com/ngntrgduc/movie-manager/releases/tag/v0.1.1)]

### Added
- CLI: filtering and adding to-watch (waiting) movie.

## [[v0.1.0](https://github.com/ngntrgduc/movie-manager/releases/tag/v0.1.0)]

### Added
- Basic web interface: Data (overview), Add, and Edit page (CRUD)
- Data stored in a CSV file
- Caching for loading data, column config, options
- Power BI Dashboard
