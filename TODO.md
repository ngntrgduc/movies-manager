## Todo
- [ ] Switch to SQLite
    - [ ] For genres, using Many-to-Many Relationship approach (junction tables)
    - display all genres of a movie (maybe using CTE), select from db and convert it to df to render 
    - [ ] cache_resource for database connection
    - [ ] Allow multiline note
    - [ ] Backup mechanism
    - [ ] Delete/Edit specific genre by SQL

- [ ] Add `restore` command to restore from backup
- [ ] Add input validation for Add and Edit page
- [ ] Genres edit page
- [ ] Movies recommendation using ML + Model Compression (quantization, prune, distillation?)
    - [ ] Using cache_resource when loading model
- [ ] Calling LLM API for smart summarize like: total watched time,... using name and year field
  - [ ] As a chatbot interface?
- [ ] Adding fzf for genres filtering in CLI


## Done
- [x] Optimize performance by using cache
- [x] change status to dropped or completed auto add date to watched date
- When changing status, also update genres, too:
- [x] CLI interface with `click`
- [x] Handle when there are no data.csv file or just inform user to create it


## Abandoned
- Pydantic integration? -> overkill, more dependency, complexity, runtime overhead
    - Pydantic’s power shines when you have lots of input sources frequent validation
    - streamlit and click already provide simple validation method, so no need for pydantic
- Add toggle in sidebar for: Widgets only show values available in the currently filtered dataset -> Too much to handle, and default filtering feel more natural
- Better (short) year filtering in CLI -> not long-term compatible, what will happen if the year 2100s come? this hard to handle
    # mask &= ((df['year'] == year) | (df['year'] % 1000 == year)) # handles short year like 25 for 2025