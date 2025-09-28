## Movie manager
A simple movies manager built with Streamlit.

Story: I originally tracked my movie-watching journey in Notion (web). But adding new movies in Notion was painful, and once I had more than 100 movies, it became laggy 🙂.
So I built this movie manager as a more convenient way to manage my movie collection.


## A glimpse
**Web interface**
![](/images/data.png)
![](/images/add.png)
![](/images/edit.png)

**Dashboard**
![](/images/dashboard.png)


## Tech stack
- UI: Streamlit
- Data: CSV file 
- Visualization: Power BI

## Features
- Data stored in CSV file
- Full CRUD support (Create, Read, Update, Delete)
- Track essential metadata: `name`, `year`, `status`, `type`, `country`, `genres`, `rating`, `watched_date`, `note`
- Interactive dashboard with Power BI (Streamlit charts are limited and less interactive compared to Power BI)

## Notes
- `kdrama` = `series` + `korea` (similarly, `cdrama` = `series` + `china`)
- `anime` = `animation` + `japan`
- `romcom` = `romance` + `comedy`
- For privacy reasons, this repo only includes a small sample of my original dataset, stored in `data/demo.csv`
- The Power BI report (`dashboard.pbix`) already contains this sample data:
    - If you want to refresh the report, update the data source to point to `data/demo.csv`

## News
- **2025-09-29**: Release `v0.1.0` - Data stored in a CSV file

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
- Run the app
```
streamlit run app.py
```

#### Happy watching 😄. But remember that movies are also a form of escapism 😢.