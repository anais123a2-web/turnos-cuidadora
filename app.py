import streamlit as st
import pandas as pd
from datetime import date
import calendar
import os

ARCHIVO = "turnos_cuidadora.csv"

USUARIOS = {
    "cuidadora": {"clave": "1234", "rol": "editar", "nombre": "Cuidadora"},
    "papa": {"clave": "1234", "rol": "ver", "nombre": "Papá"}
}

VALORES = {
    "Día completo": 20000,
    "Medio día mañana": 10000,
    "Medio día tarde": 10000,
    "Libre": 0
}

COLORES = {
    "Día completo": "#F4A261",
    "Medio día mañana": "#E9C46A",
    "Medio día tarde": "#F6BD60",
    "Libre": "#EDE0D4"
}

ICONOS = {
    "Día completo": "✅",
    "Medio día mañana": "🌤️",
    "Medio día tarde": "🌙",
    "Libre": "⚪"
}

st.set_page_config(
    page_title="Control de Turnos",
    page_icon="📅",
    layout="wide"
)

st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg, #fff7ed 0%, #ffe8d6 100%);
}

.main-title {
    text-align: center;
    font-size: 42px;
    font-weight: 900;
    color: #9c4221;
    margin-bottom: 0px;
}

.subtitle {
    text-align: center;
    font-size: 18px;
    color: #6b4f3f;
    margin-bottom: 30px;
}

.card {
    background-color: rgba(255,255,255,0.90);
    border-radius: 22px;
    padding: 22px;
    box-shadow: 0 8px 22px rgba(92, 64, 51, 0.12);
    border: 1px solid #f3d5b5;
    margin-bottom: 18px;
}

.day-card {
    background-color: white;
    border-radius: 18px;
    padding: 14px;
    min-height: 120px;
    box-shadow: 0 5px 14px rgba(92,64,51,0.10);
    border: 1px solid #f3d5b5;
}

.day-number {
    font-size: 18px;
    font-weight: 900;
    color: #7f4f24;
}

.day-status {
    font-size: 14px;
    font-weight: 700;
    color: #4a3428;
}

.day-value {
    font-size: 13px;
    color: #6b4f3f;
}

.stButton>button {
    background-color: #bc6c25;
    color: white;
    border-radius: 12px;
    font-weight: 800;
    border: none;
    padding: 10px 18px;
}

.stButton>button:hover {
    background-color: #9c4221;
    color: white;
}

[data-testid="stMetric"] {
    background-color: rgba(255,255,255,0.92);
    padding: 18px;
    border-radius: 18px;
    box-shadow: 0 6px 16px rgba(92,64,51,0.10);
    border: 1px solid #f3d5b5;
}

[data-testid="stMetricValue"] {
    color: #9c4221;
    font-weight: 900;
}

hr {
    border: none;
    border-top: 1px solid #e6ccb2;
}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">📅 Control de Turnos</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Registro mensual de jornadas, pagos y observaciones</div>', unsafe_allow_html=True)

if "logueado" not in st.session_state:
    st.session_state.logueado = False

if not st.session_state.logueado:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("🔐 Iniciar sesión")

    usuario = st.text_input("Usuario")
    clave = st.text_input("Contraseña", type="password")

    if st.button("Entrar"):
        if usuario in USUARIOS and clave == USUARIOS[usuario]["clave"]:
            st.session_state.logueado = True
            st.session_state.usuario = usuario
            st.session_state.rol = USUARIOS[usuario]["rol"]
            st.rerun()
        else:
            st.error("Usuario o contraseña incorrectos")

    st.caption("Usuarios de prueba: cuidadora / papa | Clave: 1234")
    st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

usuario = st.session_state.usuario
rol = st.session_state.rol
nombre = USUARIOS[usuario]["nombre"]

col_sesion, col_salir = st.columns([4, 1])
with col_sesion:
    st.success(f"Sesión iniciada como: {nombre} | Permiso: {'Editar' if rol == 'editar' else 'Solo lectura'}")
with col_salir:
    if st.button("Cerrar sesión"):
        st.session_state.logueado = False
        st.rerun()

hoy = date.today()

st.markdown('<div class="card">', unsafe_allow_html=True)
col1, col2 = st.columns(2)

with col1:
    mes = st.selectbox(
        "Mes",
        list(range(1, 13)),
        index=hoy.month - 1,
        format_func=lambda x: calendar.month_name[x].capitalize()
    )

with col2:
    anio = st.number_input("Año", min_value=2024, max_value=2035, value=hoy.year)

st.markdown('</div>', unsafe_allow_html=True)

dias_mes = calendar.monthrange(anio, mes)[1]

if os.path.exists(ARCHIVO):
    df_guardado = pd.read_csv(ARCHIVO)
else:
    df_guardado = pd.DataFrame(columns=["fecha", "jornada", "observacion", "valor"])

filas = []

for dia in range(1, dias_mes + 1):
    fecha_actual = date(anio, mes, dia).isoformat()
    existente = df_guardado[df_guardado["fecha"] == fecha_actual]

    if not existente.empty:
        jornada = existente.iloc[0]["jornada"]
        observacion = existente.iloc[0]["observacion"]
    else:
        jornada = "Libre"
        observacion = ""

    filas.append({
        "Fecha": fecha_actual,
        "Día": dia,
        "Jornada": jornada,
        "Observación": "" if pd.isna(observacion) else observacion,
        "Valor": VALORES.get(jornada, 0)
    })

df_mes = pd.DataFrame(filas)

st.markdown("## 🗓️ Calendario visual del mes")

dias_semana = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
cols = st.columns(7)

for i, nombre_dia in enumerate(dias_semana):
    cols[i].markdown(f"**{nombre_dia}**")

primer_dia_semana = date(anio, mes, 1).weekday()
posicion = 0

for _ in range(primer_dia_semana):
    with cols[posicion]:
        st.write("")
    posicion += 1

for _, row in df_mes.iterrows():
    jornada = row["Jornada"]
    color = COLORES.get(jornada, "#ffffff")
    icono = ICONOS.get(jornada, "")

    with cols[posicion % 7]:
        st.markdown(
            f"""
            <div class="day-card" style="border-left: 8px solid {color};">
                <div class="day-number">{int(row["Día"])} {icono}</div>
                <div class="day-status">{jornada}</div>
                <div class="day-value">${int(row["Valor"]):,}</div>
                <div style="font-size:12px;color:#7c6a5c;">{row["Observación"]}</div>
            </div>
            """.replace(",", "."),
            unsafe_allow_html=True
        )
    posicion += 1

st.markdown("---")

st.markdown("## ✏️ Registro y edición")

if rol == "editar":
    st.info("Puedes corregir jornadas y observaciones. Luego presiona guardar.")

    df_editado = st.data_editor(
        df_mes,
        use_container_width=True,
        num_rows="fixed",
        column_config={
            "Jornada": st.column_config.SelectboxColumn(
                "Jornada",
                options=list(VALORES.keys()),
                required=True
            ),
            "Valor": st.column_config.NumberColumn(
                "Valor",
                disabled=True
            )
        },
        disabled=["Fecha", "Día", "Valor"],
        hide_index=True
    )

    df_editado["Valor"] = df_editado["Jornada"].map(VALORES)

    if st.button("💾 Guardar cambios"):
        nuevo_df = df_editado.rename(columns={
            "Fecha": "fecha",
            "Jornada": "jornada",
            "Observación": "observacion",
            "Valor": "valor"
        })

        nuevo_df = nuevo_df[["fecha", "jornada", "observacion", "valor"]]

        df_guardado = df_guardado[~df_guardado["fecha"].isin(nuevo_df["fecha"])]
        df_final = pd.concat([df_guardado, nuevo_df], ignore_index=True)
        df_final.to_csv(ARCHIVO, index=False)

        st.success("Cambios guardados correctamente")
        st.rerun()

else:
    st.warning("Este usuario solo puede ver. No puede modificar información.")
    df_editado = df_mes
    st.dataframe(df_editado, use_container_width=True, hide_index=True)

total = int(df_editado["Valor"].sum())

st.markdown("## 💰 Resumen mensual")

c1, c2, c3, c4, c5 = st.columns(5)

c1.metric("Días completos", int((df_editado["Jornada"] == "Día completo").sum()))
c2.metric("Mañanas", int((df_editado["Jornada"] == "Medio día mañana").sum()))
c3.metric("Tardes", int((df_editado["Jornada"] == "Medio día tarde").sum()))
c4.metric("Días libres", int((df_editado["Jornada"] == "Libre").sum()))
c5.metric("Total a pagar", f"${total:,.0f}".replace(",", "."))

st.markdown("## 📌 Leyenda")

l1, l2, l3, l4 = st.columns(4)
l1.markdown("✅ **Día completo:** $20.000")
l2.markdown("🌤️ **Medio día mañana:** $10.000")
l3.markdown("🌙 **Medio día tarde:** $10.000")
l4.markdown("⚪ **Libre:** $0")

csv = df_editado.to_csv(index=False).encode("utf-8")

st.download_button(
    "⬇️ Descargar reporte mensual",
    data=csv,
    file_name=f"reporte_turnos_{mes}_{anio}.csv",
    mime="text/csv"
)