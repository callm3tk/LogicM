import streamlit as st
import pandas as pd
from sqlalchemy import create_engine

engine = create_engine("sqlite:///data.db")

st.title("🌱 Smart Watering Dashboard")

df = pd.read_sql("SELECT * FROM logs", engine)

st.write("### Latest Data")
st.dataframe(df.tail())

st.write("### Charts")

st.line_chart(df[['soil', 'temp', 'hum']])
st.line_chart(df['mist'])