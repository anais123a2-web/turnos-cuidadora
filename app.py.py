import streamlit as st
import pandas as pd
from datetime import date

st.title("Registro de Turnos")

fecha = st.date_input("Selecciona la fecha", date.today())

jornada = st.selectbox("Tipo de jornada", [
    "Día completo",
    "Medio día mañana",
    "Medio día tarde",
    "Libre"
])

valores = {
    "Día completo": 20000,
    "Medio día mañana": 10000,
    "Medio día tarde": 10000,
    "Libre": 0
}

observacion = st.text_area("Observación")

if st.button("Guardar"):
    data = {
        "fecha": fecha,
        "jornada": jornada,
        "valor": valores[jornada],
        "observacion": observacion
    }

    df = pd.DataFrame([data])

    try:
        df_old = pd.read_csv("datos.csv")
        df = pd.concat([df_old, df])
    except:
        pass

    df.to_csv("datos.csv", index=False)

    st.success("Guardado correctamente")

st.subheader("Registros")

try:
    df = pd.read_csv("datos.csv")
    st.dataframe(df)
    st.write("Total:", df["valor"].sum())
except:
    st.write("Aún no hay datos")