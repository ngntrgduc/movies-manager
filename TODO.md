## Todo
- [ ] Switch to SQLite
    - [ ] CRUD operation
    - [ ] select from database and convert it to df to render in streamlit
    - [ ] cache_resource for database connection
    - [ ] Allow multiline note, CSV doesn't work well with multiline note
    - [ ] Backup mechanism
    - [ ] Delete/Edit specific genre by SQL
    - [ ] Using sql for `stats` command, avoid reading full data compare to current method (read csv using pandas)
        - [ ] Keep `stats` functionality for filtered data instead of using sql
    - [ ] Edit genres of a movie only
- [ ] Add input validation for Add and Edit page
- [ ] Genres edit page
- [ ] Movies recommendation using ML + Model Compression (quantization, prune, distillation?)
    - [ ] Using cache_resource when loading model
- [ ] Calling LLM API for smart summarize like: total watched time,... using name and year field
  - [ ] As a chatbot interface?
- [ ] Adding fzf for genres filtering in CLI
- [ ] Back up & restore functionality for web app?
- [ ] utils.genre -> str_to_list, list_to_str conversion
- [ ] Edit/Update movie functionality for CLI
- [ ] Add simple filtering mechanism for Edit page, easier to edit instead of scrolling. Does this add conflict rendering when filtering???

## Done
- [x] Optimize performance by using cache
- [x] change status to dropped or completed auto add date to watched date
- [x] CLI interface with `click`
- [x] Add `restore` command to restore from backup
- [x] Prevent display all movies in CLI: when run with only flags, for example `py cli filter --stats`, it will display all movies -> bad CLI UX


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
- Better (short) year filtering in CLI -> not long-term compatible, what will happen if the year 2100s come? this hard to handle
    - ```# mask &= ((df['year'] == year) | (df['year'] % 1000 == year)) # handles short year like 25 for 2025```