import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "data.db")
engine = create_engine(f"sqlite:///{DB_PATH}")

st.title("🌱 Smart Watering Dashboard")

df = pd.read_sql("SELECT * FROM logs", engine)

st.write("### Latest Data")
st.dataframe(df.tail())

st.write("### Charts")

st.line_chart(df[['soil', 'temp', 'hum']])
st.line_chart(df['mist'])