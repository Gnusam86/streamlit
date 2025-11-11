# app.py
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import io
from datetime import datetime
import time

st.set_page_config(page_title="Simulador avanzado de tramos", layout="wide")

# ---------------------------
# Funciones utilitarias
# ---------------------------
def generar_tramos_ejemplo(preset):
    if preset == "Ruta urbana":
        return pd.DataFrame({"tramo": [1,2,3,4,5], "distancia_m": [120, 300, 80, 200, 150]})
    if preset == "Ruta deportiva":
        return pd.DataFrame({"tramo": [1,2,3,4], "distancia_m": [500, 800, 400, 600]})
    if preset == "Ruta mixta":
        return pd.DataFrame({"tramo": [1,2,3,4,5,6], "distancia_m": [100, 250, 50, 400, 180, 220]})
    return pd.DataFrame({"tramo":[1,2,3], "distancia_m":[100,100,100]})

def calcular_tiempos(df, velocidades_m_s):
    df = df.copy()
    df["velocidad_m_s"] = velocidades_m_s
    # proteger división por cero
    df["velocidad_m_s"] = df["velocidad_m_s"].replace(0, np.nan)
    df["tiempo_s"] = df["distancia_m"] / df["velocidad_m_s"]
    df["tiempo_s"] = df["tiempo_s"].fillna(np.inf)
    df["tiempo_acum_s"] = df["tiempo_s"].cumsum()
    df["velocidad_kmh"] = df["velocidad_m_s"] * 3.6
    return df

def resumen_metrics(df):
    total_time = df["tiempo_s"].replace(np.inf, np.nan).sum()
    avg_speed = (df["distancia_m"].sum() / total_time) if total_time and total_time>0 else 0
    max_speed = df["velocidad_m_s"].max()
    min_speed = df["velocidad_m_s"].min()
    return {
        "Tiempo total (s)": total_time if not np.isnan(total_time) else float("nan"),
        "Velocidad media (m/s)": avg_speed,
        "Velocidad máxima (m/s)": max_speed,
        "Velocidad mínima (m/s)": min_speed
    }

def df_to_csv_bytes(df):
    towrite = io.BytesIO()
    df.to_csv(towrite, index=False)
    towrite.seek(0)
    return towrite

# ---------------------------
# Sidebar: datos, presets, controls
# ---------------------------
st.sidebar.title("Controles")
modo_entrada = st.sidebar.radio("Origen de datos", ["Cargar CSV", "Usar preset", "Generador aleatorio"])

df_base = None  # inicializar

if modo_entrada == "Cargar CSV":
    uploaded = st.sidebar.file_uploader("Sube CSV con columnas: tramo, distancia_m", type=["csv"])
    if uploaded is not None:
        try:
            df_base = pd.read_csv(uploaded)
        except Exception as e:
            st.sidebar.error(f"No se pudo leer el CSV: {e}")
            st.stop()
        required = {"tramo", "distancia_m"}
        if not required.issubset(set(df_base.columns)):
            st.sidebar.error("El CSV debe tener columnas 'tramo' y 'distancia_m'.")
            st.stop()
        df_base["distancia_m"] = pd.to_numeric(df_base["distancia_m"], errors="coerce")
        if df_base["distancia_m"].isna().any():
            st.sidebar.error("La columna 'distancia_m' contiene valores no numéricos.")
            st.stop()
    else:
        st.sidebar.warning("Aún no ha subido un CSV. Cambia a 'Usar preset' o sube un archivo.")
        st.stop()

elif modo_entrada == "Usar preset":
    preset = st.sidebar.selectbox("Preset de ejemplo", ["Ruta urbana", "Ruta deportiva", "Ruta mixta"])
    df_base = generar_tramos_ejemplo(preset)

elif modo_entrada == "Generador aleatorio":
    n = st.sidebar.slider("Número de tramos", 3, 10, 5)
    seed = st.sidebar.number_input("Semilla (opcional)", value=42, step=1)
    rng = np.random.default_rng(int(seed))
    distances = list((rng.integers(50, 600, size=n)).astype(int))
    df_base = pd.DataFrame({"tramo": list(range(1, n+1)), "distancia_m": distances})

# protección final
if df_base is None or df_base.empty:
    st.error("No hay datos para mostrar. Seleccione un origen de datos válido en la barra lateral.")
    st.stop()

st.sidebar.markdown("---")
st.sidebar.subheader("Comparador (hasta 3)")
num_configs = st.sidebar.selectbox("Nº configuraciones a comparar", [1,2,3], index=1)

# Presets para cada configuración
configs = {}
for i in range(1, num_configs+1):
    st.sidebar.markdown(f"**Configuración {i}**")
    name = st.sidebar.text_input(f"Nombre {i}", value=f"Config {i}", key=f"name{i}")
    mode = st.sidebar.selectbox(f"Modo velocidad {i}", ["Manual por tramo", "Velocidad uniforme"], key=f"mode{i}")
    if mode == "Velocidad uniforme":
        v = st.sidebar.slider(f"Velocidad uniforme {i} (m/s)", 1.0, 30.0, 8.0 + (i-1)*2.0, key=f"vu{i}")
        speeds = [v] * len(df_base)
    else:
        speeds = None
    configs[i] = {"name": name, "mode": mode, "speeds": speeds}

st.sidebar.markdown("---")
st.sidebar.subheader("Acciones")
if st.sidebar.button("Cargar presets por defecto"):
    st.experimental_set_query_params(_preset_load=int(time.time()))
    st.experimental_rerun_available = False  # no-op flag for clarity

export_csv = st.sidebar.checkbox("Habilitar exportar CSV", value=True)
st.sidebar.info("Usa el panel principal para ajustar velocidades manuales si eliges ese modo.")

# ---------------------------
# Main: presentación y edición manual
# ---------------------------
st.title("Simulador didáctico de tramos — Universidad Hipócrates")
st.markdown("Mtro. Samuel Alvarado — Visualiza y compara hasta 3 configuraciones en tiempo real")

col1, col2 = st.columns([2,1])

with col1:
    st.subheader("Datos base")
    st.dataframe(df_base.reset_index(drop=True), width="stretch")

with col2:
    st.subheader("Resumen base")
    st.metric("Tramos", int(len(df_base)))
    st.metric("Distancia total (m)", int(df_base["distancia_m"].sum()))

st.markdown("---")
st.subheader("Ajuste de velocidades por configuración")

# Panel para editar velocidades manualmente si corresponde
manual_inputs = {}
for i in range(1, num_configs+1):
    cfg = configs[i]
    st.markdown(f"### {cfg['name']}")
    if cfg["mode"] == "Velocidad uniforme":
        st.write(f"Velocidad uniforme: **{cfg['speeds'][0]} m/s**")
        manual_inputs[i] = cfg['speeds']
    else:
        st.write("Ingrese velocidad por tramo (m/s):")
        n_cols = min(len(df_base), 6)
        cols = st.columns(n_cols)
        speeds = []
        for idx, tramo in enumerate(df_base["tramo"].tolist()):
            col = cols[idx % n_cols]
            default_v = 8.0
            key_input = f"t{tramo}_i{i}"
            v = col.number_input(key_input, min_value=0.1, max_value=50.0, value=float(default_v), step=0.1, key=key_input+"_ui")
            speeds.append(v)
        manual_inputs[i] = speeds

# ---------------------------
# Cálculo de resultados por configuración
# ---------------------------
results = {}
for i in range(1, num_configs+1):
    speeds = manual_inputs.get(i)
    if speeds is None or len(speeds) != len(df_base):
        speeds = [8.0] * len(df_base)
    df_res = calcular_tiempos(df_base, speeds)
    results[i] = df_res

# ---------------------------
# Mostrar métricas comparativas
# ---------------------------
st.markdown("---")
st.subheader("Métricas comparativas")

metrics_cols = st.columns(num_configs)
for i, col in enumerate(metrics_cols, start=1):
    with col:
        st.markdown(f"**{configs[i]['name']}**")
        mets = resumen_metrics(results[i])
        total_display = "N/A" if not np.isfinite(mets["Tiempo total (s)"]) else f"{mets['Tiempo total (s)']:.2f}"
        st.metric("Tiempo total (s)", total_display)
        st.metric("Vel media (m/s)", f"{mets['Velocidad media (m/s)']:.2f}")
        st.metric("Vel máx (m/s)", f"{mets['Velocidad máxima (m/s)']:.2f}")

# ---------------------------
# Visualizaciones interactivas
# ---------------------------
st.markdown("---")
st.subheader("Visualizaciones")

fig1 = go.Figure()
colors = ["#1f77b4", "#ff7f0e", "#2ca02c"]
for i in range(1, num_configs+1):
    df_r = results[i]
    fig1.add_trace(go.Scatter(x=df_r["tramo"], y=df_r["tiempo_acum_s"], mode="lines+markers",
                              name=configs[i]["name"], marker=dict(color=colors[i-1])))
fig1.update_layout(title="Tiempo acumulado por tramo", xaxis_title="Tramo", yaxis_title="Tiempo acumulado (s)")
st.plotly_chart(fig1, width="stretch")

fig2 = go.Figure()
for i in range(1, num_configs+1):
    df_r = results[i]
    fig2.add_trace(go.Bar(x=df_r["tramo"], y=df_r["velocidad_kmh"], name=configs[i]["name"], marker_color=colors[i-1], opacity=0.7))
fig2.update_layout(barmode='group', title="Velocidad por tramo (km/h)", xaxis_title="Tramo", yaxis_title="Velocidad (km/h)")
st.plotly_chart(fig2, width="stretch")

fig3 = go.Figure()
for i in range(1, num_configs+1):
    fig3.add_trace(go.Box(y=results[i]["tiempo_s"].replace(np.inf, np.nan), name=configs[i]["name"], marker_color=colors[i-1]))
fig3.update_layout(title="Distribución de tiempo por tramo", yaxis_title="Tiempo por tramo (s)")
st.plotly_chart(fig3, width="stretch")

# Tabla detallada por configuración con opción de selección
st.markdown("---")
st.subheader("Tabla detallada (selecciona configuración)")
sel = st.selectbox("Mostrar resultados de:", [configs[i]["name"] for i in range(1, num_configs+1)], index=0)
sel_idx = next(i for i in range(1, num_configs+1) if configs[i]["name"] == sel)
st.dataframe(results[sel_idx].reset_index(drop=True), width="stretch")

# ---------------------------
# Exportar resultados y opciones de presentación
# ---------------------------
st.markdown("---")
st.subheader("Exportar y presentación")

if export_csv:
    for i in range(1, num_configs+1):
        csv_bytes = df_to_csv_bytes(results[i])
        filename = f"{configs[i]['name'].replace(' ', '_')}_resultados_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        st.download_button(label=f"Descargar CSV - {configs[i]['name']}", data=csv_bytes, file_name=filename, mime="text/csv")

st.markdown("**Controles rápidos para exposición:**")
if st.button("Restablecer valores (recargar página)"):
    # limpiar session state
    for k in list(st.session_state.keys()):
        del st.session_state[k]
    # forzar rerun cambiando un query param
    st.experimental_set_query_params(_reset=int(time.time()))

st.info("Para la exposición prepara 3 presets con datos reales y usa el comparador para mostrar mejoras entre configuraciones.")

st.markdown("---")
st.caption("Versión demostrativa. Adapta variables, presets y visualizaciones según el objetivo pedagógico.")
