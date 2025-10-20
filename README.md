## Movies manager
A simple movies manager built with Streamlit.

Story: I originally tracked my movie-watching journey in Notion (web). But adding new movies in Notion was painful, and once I had more than 100 movies, it became laggy 🙂.
So I built this movies manager as a more convenient way to manage my movie collection.

## Tech stack
- UI: Streamlit
- Data: CSV file 
- Visualization: Power BI
- CLI: Click + Rich

## Features
- Full CRUD support (Create, Read, Update, Delete)
- Track essential metadata: `name`, `year`, `status`, `type`, `country`, `genres`, `rating`, `watched_date`, `note`
- Interactive dashboard with Power BI (Streamlit charts are limited and less interactive compared to Power BI)
- Small CLI for filtering and adding movies

## A glimpse
**Web interface**
![](/images/data.png)
![](/images/add.png)
![](/images/edit.png)

**Dashboard**
![](/images/dashboard.png)

## Notes
- `kdrama` = `series` + `Korea` (similarly, `cdrama` = `series` + `China`)
- `anime` = `animation` + `Japan`
- `romcom` = `romance` + `comedy`
- For privacy reasons, this repo only includes a small sample of my original dataset, stored in `data/data.csv`.
- Remember to refresh all tables to get the latest data in the Power BI report (`dashboard.pbix`).
- Click is bad at handling clickable links, so it recommended to view notes in Streamlit web version instead of CLI.

## Recent updates
- `v0.1.2` - Improved CLI
- `v0.1.1` - Added small CLI
- `v0.1.0` - Data stored in a CSV file

## Usage
- Install [uv](https://docs.astral.sh/uv/) (recommended for package management)
- Create a virtual environment
```
uv venv
```
- Activate the virtual environment
- Sync dependencies
```
uv sync
```
- Or sync dependencies with CLI support
```
uv sync --extra cli
```
- Run the app
```
streamlit run app.py
```
- Run the CLI (if installed with `--extra cli`):
```
py cli.py
```
```
Usage: cli.py [OPTIONS] COMMAND [ARGS]...

  Command-line tool to manage, filter, and analyze your movie collection.

Options:
  -h, --help  Show this message and exit.

Commands:
  add     Add a new movie interactively.
  backup  Back up data.
  filter  Filter movies by attributes.
  stats   Show statistics for the movie data.
```

## TODO
- [ ] Switch to SQLite
    - [ ] cache_resource for database connection
    - [ ] Allow multiline note
    - [ ] Backup mechanism
    - [ ] Delete/Edit specific genre
- [ ] Add input validation for Add and Edit page
- [ ] Movies recommendation using ML + Model Compression
- [ ] Calling LLM API for smart summarize like: total watched time,... using name and year field
  - [ ] As a chatbot interface?

#### Happy watching 😄. But remember that movies are also a form of escapism 😢.