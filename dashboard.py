import streamlit as st
import pandas as pd
import os

st.title("📊 Dashboard")

if not os.path.exists("data.csv"):
    st.warning("Belum ada data")
    st.stop()

df = pd.read_csv("data.csv")
st.dataframe(df)
