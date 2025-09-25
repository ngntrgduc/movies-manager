import streamlit as st

pg = st.navigation(
    [
        st.Page("pages/1_data.py", title="Data"),  # number before name for ordering purpose
        st.Page("pages/add_movie.py", title="Add"),
        st.Page("pages/edit_movie.py", title="Edit"),
    ],
    position="top"
)
pg.run()