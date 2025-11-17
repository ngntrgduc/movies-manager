import streamlit as st

pg = st.navigation(
    [
        st.Page("pages/1_data.py", title="Data"),  # number before name for ordering purpose
        st.Page("pages/2_add_movie.py", title="Add"),
        st.Page("pages/3_edit_movie.py", title="Edit"),
    ],
    position="top"
)
pg.run()