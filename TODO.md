## Todo
- [ ] Movies recommendation using ML + Model Compression (quantization, prune, distillation?)
    - [ ] Using cache_resource when loading model
    - [ ] Collect data: movielens?
    - [ ] Data processing
        Use content-based filtering by computing similarity between movies.
    - [ ] Use recent watched genres to recommend movies with waiting status
    - [ ] Dimension reduction if it slow (SVD, PCA)
    - [ ] NLP for plot summaries? TF-IDF? -> recommend movies based on their plots summaries
        Why not TF-IDF? TF-IDF downweights words that appear frequently (like "Action"). In movie recommendations, if you love "Action", you want that word to carry heavy weight.
    - [ ] Using `recommend` for recommendation in CLI? or in web app? or .ipynb?
    - [ ] Using LLM to create Overview of movie by name, year, country?, to create plot soup?
    - Note field need NLP to extract useful information -> sentiment analysis?
- [ ] Calling LLM API for smart summarize like: total watched time,... using name and year field
  - [ ] As a chatbot interface?
- [ ] Add testing for csv_to_sqlite and CRUD operations on database logic, using pytest, `:memory:` for testing with sqlite
    - [ ] Running all the tests by using `check` command in CLI
- [ ] Add another table for watched movies in the past (long time ago) but don't remember the date exactly. Maybe just contains: id, name, year, country.

### CLI
- [ ] CLI demo as GIF and put it in README
- [ ] genres subcommand, contain: list (list all genres with id), delete genre, update/edit genres, clean genres (unused genres like 'test', but maybe now this is unecessary because of ON DELETE CASCADE)
- [ ] Alias commands (prefix match + fuzzy matching), better and faster UX, less to type
- [ ] Allow to type id for update/delete command if not provided
- [ ] Allow `resolve_choice` to handle same initials, when the data scaled (more countries, etc.)
- [ ] Allow adding new country for `add` and `update` command

### Web App
- [ ] Add input validation for Add and Edit pages
    - [ ] Year, date, rating validation 
- [ ] Genres edit/delete page
- [ ] Back up & restore functionality for web app, with confirmation dialog
    - [ ] Show last modified backup date
    - [ ] Show toast when complete
- [ ] SQL page for web app, select script, show dataframe
    - [ ] Show SQL code in file, using st.code(query, language='sql')
    - left col: script select + run button(?) + sql code display; right col: dataframe

### Dashboard
- [ ] Allow it to use sqlite database instead of csv -> faster CLI experience
    - [ ] Then add `csv` to update the csv file for quick overview, remove `update_csv` in CLI app
- [ ] Handle countries distribution pie chart: only show top 4 countries with largest number of movies, others will be labeled as "Other" (include None)

## Done
- [x] Optimize performance by using cache
- [x] change status to dropped or completed auto add date to watched date
- [x] CLI interface with `click`
- [x] Add `restore` command to restore from backup
- [x] Prevent display all movies in CLI: when run with only flags, for example `py cli filter --stats`, it will display all movies -> bad CLI UX
- [x] Allow CLI run SQL scripts? like `py cli.py sql <script>` for quickly query (`py cli.py sql thismonth` list all watched movie in this month, `py cli.py sql watched` list all completed and dropped movie, faster, more flexible, more user customizable, scripts will placed in `sql/` folder)
    - [x] If no script given, print all scripts (exclude `schema.sql`)
- [x] Edit/Update movie functionality for CLI
- [x] Switch to SQLite
    - [x] CRUD operation
    - [x] Backup/Restore mechanism
    - [x] Fix SQLite compatibility with None value
    - [x] Using sql for `stats` command, avoid reading full data compare to current method (read csv using pandas)
    - [x] Add show id checkbox for web ui in Filtering page
- [x] Change web app Edit page layout, add Refresh button
- [x] Add fuzzy matching with genre filtering if there is no match for genre name in the CLI
- [x] Add `--sort` flag for `sql` command
    - [x] Allow inputting asc and desc and its alias for order (default is asc)
- [x] Fuzzy match for sql file for `sql` command
- [x] `--csv` option for `backup` command, for writing data to data/backup.csv with the default backup behavior, offer safer recovery
- [x] For sql command, develop another print_df function but not import and using pandas when there is no filtering like sort or show note, better performance: `print_rows`
- [x] Searches name + note in one command: `search`
- [x] Using SQL instead of pandas filtering in `filter` command
- [x] Move hard-coded type, statuses, and countries to `utils/constants.py`

## Abandoned
- Color for dataframe using pandas Styler -> Pandas Styler does not compatible with streamlit dataframe, keep it simple
- Data versioning (like DVC) -> overkill for small data, even it has advantage when develop recommender system later on
- Show all movies in CLI -> Bad UX, especially with `--note` flag
- CLI autocompletion -> too complicated, source: https://click.palletsprojects.com/en/stable/shell-completion/
- ORM -> for SQL educational purpose, also less dependency, less bug
- Pydantic integration? -> overkill, more dependency, complexity, runtime overhead
    - Pydantic’s power shines when you have lots of input sources frequent validation
    - streamlit and click already provide simple validation method, so no need for pydantic
- Add toggle in sidebar for: Widgets only show values available in the currently filtered dataset -> Too much to handle, and default filtering feel more natural
- Better (short) year filtering in CLI -> not long-term compatible, what will happen if the year 2100s come? this is hard to handle
    - ```# mask &= ((df['year'] == year) | (df['year'] % 1000 == year)) # handles short year like 25 for 2025```
- Using SQL instead of pandas filtering for `--stats` flag in `filter` command  -> Too complex in query handle and building, harder to maintain
- Make `sql` command compatible with filters: `py cli.py sql korea -g romance` -> Too much to handle, but may consider sorting flag instead of filters
- @st.cache_resource for sqlite database connection -> sqlite is not thread-safe, and streamlit is multi-threaded
- Use fzf for genres filtering in CL -> more dependency, also CLI is used for quick filtering, for better UX, go to web app
- Filtering using SQL for Data page -> using pandas does not significant slower than filtering using SQL, and often faster than SQL
- Add simple filtering mechanism for Edit page -> Ctrl + F is enough
- Add `--group` option for filter command, in rich.Table add line to separate it using add_section() -> hard to implement, complex and harder to maintaino
- Enable operator filtering, like filter --year >=8 or something like that
- Paging -> A personal movies collection hardly exceed 10K movies, and Paging method only shine when dealing with database contains million of rows. Also, it's all about UI/UX
- Implement auto copy old value for current field in `update` command -> this is bad in term of security, also user can select and ctrl + C, a bit of work but improve maintainance, reduce code complexity