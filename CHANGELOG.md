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
