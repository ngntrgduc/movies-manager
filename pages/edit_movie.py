import streamlit as st
import pandas as pd

from ast import literal_eval

from utils.data import load_data, load_column_config

st.set_page_config(page_title = "Edit movies", page_icon=":pencil2:", layout="wide")

def prepare_for_save(df: pd.DataFrame) -> pd.DataFrame:
    # Convert list of genres as string to list of genres
    df["genres"] = df["genres"].apply(
        lambda g: ','.join(literal_eval(g)) 
        if isinstance(g, str) and (g.startswith('[') and g.endswith(']')) else g
    )
    return df


df = load_data()
edited_df = st.data_editor(
    df,
    column_config=load_column_config(),
    hide_index=True,
    num_rows="dynamic",
)

if st.button(
    "Update", 
    help="Streamlit reruns on every widget interaction. \
    When editing data, double-click to update the database."
):
    saved_df = prepare_for_save(edited_df.copy())
    saved_df.to_csv("test.csv", index=False)
    st.toast("Updated database.", icon='✅')