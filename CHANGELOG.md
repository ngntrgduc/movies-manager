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

## [[v0.1.2](https://github.com/ngntrgduc/movies-manager/releases/tag/v0.1.2)]

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

## [[v0.1.1](https://github.com/ngntrgduc/movies-manager/releases/tag/v0.1.1)]

### Added
- CLI: filtering and adding to-watch (waiting) movie.

## [[v0.1.0](https://github.com/ngntrgduc/movies-manager/releases/tag/v0.1.0)]

### Added
- Basic web interface: Data (overview), Add, and Edit page (CRUD)
- Data stored in a CSV file
- Caching for loading data, column config, options
- Power BI Dashboard
