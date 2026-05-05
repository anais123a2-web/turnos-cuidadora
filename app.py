import streamlit as st
import pandas as pd
from datetime import date
import calendar
import os

ARCHIVO = "turnos_cuidadora.csv"

USUARIOS = {
    "cuidadora": {"clave": "1234", "rol": "editar", "nombre": "Cuidadora"},
    "papa": {"clave": "1234", "rol": "ver", "nombre": "Papá"},
}

VALORES = {
    "Día completo": 20000,
    "Medio día mañana": 10000,
    "Medio día tarde": 10000,
    "Libre": 0,
}

COLORES = {
    "Día completo": "#F4A261",
    "Medio día mañana": "#E9C46A",
    "Medio día tarde": "#F6BD60",
    "Libre": "#EDE0D4",
}

ICONOS = {
    "Día completo": "✅",
    "Medio día mañana": "🌤️",
    "Medio día tarde": "🌙",
    "Libre": "⚪",
}

st.set_page_config(page_title="Control de Turnos", page_icon="📅", layout="wide")

st.markdown(
    """
<style>
.stApp {
    background:
        radial-gradient(circle at 10% 20%, rgba(255, 200, 200, 0.25), transparent 40%),
        radial-gradient(circle at 90% 80%, rgba(200, 220, 255, 0.25), transparent 40%),
        linear-gradient(135deg, #ffffff 0%, #f8f9fb 100%);
}

html, body, [class*="css"] {
    font-family: 'Segoe UI', 'Poppins', sans-serif;
    color: #111827;
}

.main-title {
    text-align: center;
    font-size: 40px;
    font-weight: 900;
    color: #111827;
    margin-bottom: 0px;
}

.subtitle {
    text-align: center;
    font-size: 16px;
    color: #4b5563;
    margin-bottom: 25px;
}

.card {
    background-color: rgba(255,255,255,0.96);
    border-radius: 22px;
    padding: 22px;
    box-shadow: 0 8px 20px rgba(0,0,0,0.06);
    border: 1px solid #e5e7eb;
    margin-bottom: 20px;
}

.day-card {
    background-color: white;
    border-radius: 18px;
    padding: 16px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.06);
    border: 1px solid #e5e7eb;
    margin-bottom: 14px;
}

.day-number {
    font-size: 20px;
    font-weight: 900;
    color: #111827;
}

.day-status {
    font-size: 14px;
    font-weight: 700;
    color: #374151;
}

.day-value {
    font-size: 14px;
    color: #374151;
    font-weight: 700;
}

.stButton > button {
    background: linear-gradient(135deg, #6366f1, #4f46e5);
    color: white;
    border-radius: 16px;
    font-weight: 800;
    border: none;
    padding: 14px 18px;
    font-size: 16px;
    width: 100%;
    transition: all 0.2s ease;
}

.stButton > button:hover {
    transform: scale(1.01);
    background: linear-gradient(135deg, #4f46e5, #4338ca);
    color: white;
}

input, textarea, select {
    border-radius: 12px !important;
}

[data-testid="stMetric"] {
    background-color: white;
    padding: 16px;
    border-radius: 16px;
    border: 1px solid #e5e7eb;
}

[data-testid="stMetricValue"] {
    color: #111827;
    font-weight: 900;
}

@media (max-width: 768px) {
    .main-title { font-size: 32px; }
    .subtitle { font-size: 14px; }
    .card { padding: 16px; }
    .day-card { padding: 16px; }
}
</style>
""",
    unsafe_allow_html=True,
)

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
    if st.button("Salir"):
        st.session_state.logueado = False
        st.rerun()

hoy = date.today()

st.markdown('<div class="card">', unsafe_allow_html=True)
st.subheader("📆 Seleccionar periodo")
col1, col2, col3 = st.columns([2, 1, 1])
with col1:
    mes = st.selectbox(
        "Mes",
        list(range(1, 13)),
        index=hoy.month - 1,
        format_func=lambda x: calendar.month_name[x].capitalize(),
    )
with col2:
    anio = st.number_input("Año", min_value=2024, max_value=2035, value=hoy.year)
with col3:
    vista = st.radio("Vista", ["📱 Móvil", "💻 PC"], horizontal=False)
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
        "Valor": VALORES.get(jornada, 0),
    })

df_mes = pd.DataFrame(filas)

st.markdown("## 🗓️ Calendario visual del mes")

if vista == "📱 Móvil":
    for _, row in df_mes.iterrows():
        jornada = row["Jornada"]
        color = COLORES.get(jornada, "#ffffff")
        icono = ICONOS.get(jornada, "")
        valor = f"${int(row['Valor']):,}".replace(",", ".")

        st.markdown(
            f"""
            <div class="day-card" style="border-left: 8px solid {color};">
                <div class="day-number">📅 Día {int(row['Día'])} {icono}</div>
                <div style="
                    margin-top:8px;
                    padding:7px 11px;
                    display:inline-block;
                    border-radius:12px;
                    background-color:{color};
                    font-size:13px;
                    font-weight:800;
                    color:#111827;
                ">{jornada}</div>
                <div class="day-value" style="margin-top:10px;">💰 {valor}</div>
                <div style="font-size:13px;color:#6b7280;margin-top:6px;">{row['Observación']}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
else:
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
        valor = f"${int(row['Valor']):,}".replace(",", ".")

        with cols[posicion % 7]:
            st.markdown(
                f"""
                <div class="day-card" style="border-left: 8px solid {color};">
                    <div class="day-number">{int(row['Día'])} {icono}</div>
                    <div class="day-status">{jornada}</div>
                    <div class="day-value">{valor}</div>
                    <div style="font-size:12px;color:#6b7280;">{row['Observación']}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        posicion += 1

st.markdown("---")
st.markdown("## ✏️ Registro rápido de turnos")

if rol == "editar":
    st.info("Selecciona un día, elige la jornada y guarda los cambios.")

    dia_seleccionado = st.selectbox(
        "📅 Selecciona el día",
        df_mes["Día"].tolist(),
        format_func=lambda x: f"Día {x}",
    )

    fila_actual = df_mes[df_mes["Día"] == dia_seleccionado].iloc[0]
    valor_actual = f"${int(fila_actual['Valor']):,}".replace(",", ".")

    st.markdown(
        f"""
        <div class="card">
            <h3 style="color:#111827; margin-top:0;">📅 Día {int(fila_actual['Día'])}</h3>
            <p style="color:#374151; font-size:15px;">
                Jornada actual: <b>{fila_actual['Jornada']}</b><br>
                Valor actual: <b>{valor_actual}</b>
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    nueva_jornada = st.radio(
        "Selecciona jornada",
        list(VALORES.keys()),
        index=list(VALORES.keys()).index(fila_actual["Jornada"]),
        horizontal=False,
    )

    nueva_observacion = st.text_area(
        "Observación",
        value=fila_actual["Observación"],
        placeholder="Ej: llegó más tarde, día cambiado, pago pendiente...",
    )

    if st.button("💾 Guardar este día"):
        fecha_actual = fila_actual["Fecha"]

        nuevo_registro = pd.DataFrame([{
            "fecha": fecha_actual,
            "jornada": nueva_jornada,
            "observacion": nueva_observacion,
            "valor": VALORES[nueva_jornada],
        }])

        df_guardado = df_guardado[df_guardado["fecha"] != fecha_actual]
        df_final = pd.concat([df_guardado, nuevo_registro], ignore_index=True)
        df_final.to_csv(ARCHIVO, index=False)

        st.success("Día guardado correctamente")
        st.rerun()

    st.markdown("### 📋 Vista completa del mes")
    df_editado = df_mes.copy()
    st.dataframe(df_editado, use_container_width=True, hide_index=True)
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
c4.metric("Libres", int((df_editado["Jornada"] == "Libre").sum()))
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
    mime="text/csv",
)
