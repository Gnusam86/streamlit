import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import io

#  Estilo visual personalizado con tonos verdes
st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(to bottom right, #388e3c, #ffffff);
        color: #388e3c;
        font-family: 'Segoe UI', sans-serif;
    }
    h1, h2, h3 {
        color: #2e7d32;
    }
    .stSlider > div > div {
        background: #a5d6a7;
    }
    .stButton>button {
        background-color: #66bb6a;
        color: white;
        border-radius: 8px;
    }
    </style>
""", unsafe_allow_html=True)

#  Título del simulador
st.title(" Simulador de crecimiento de plantas")

#  Parámetros de entrada
st.header(" Parámetros de entrada")
P0 = st.number_input("Tamaño inicial de la planta (m)", min_value=0.01, max_value=5.0, value=0.1, step=0.01)
Pmax = st.number_input("Tamaño máximo de la planta (m)", min_value=0.5, max_value=10.0, value=2.0, step=0.1)
r = st.slider("Tasa de crecimiento (r)", min_value=0.01, max_value=1.0, value=0.1, step=0.01)

#  Factores ambientales
st.subheader(" Factores ambientales")
L = st.slider("Intensidad de luz (L)", 0.0, 1.0, 1.0)
N = st.slider("Disponibilidad de nutrientes (N)", 0.0, 1.0, 1.0)
W = st.slider("Agua disponible (W)", 0.0, 1.0, 1.0)

# ⏱️ Tiempo de simulación
st.header("⏱️ Tiempo de simulación")
dias = st.slider("Duración (días)", min_value=10, max_value=365, value=100, step=10)
paso = st.selectbox("Resolución temporal", options=["Diaria", "Semanal"])
dt = 1 if paso == "Diaria" else 7

# 📈 Cálculo del crecimiento
st.header("📈 Resultados del crecimiento")
r_ajustada = r * L * N * W
t = np.linspace(0, dias, int(dias/dt)+1)
P = Pmax / (1 + ((Pmax - P0) / P0) * np.exp(-r_ajustada * t))
dP_dt = r_ajustada * P * (1 - P / Pmax)

# Métricas clave
st.metric("Tamaño final estimado", f"{P[-1]:.2f} m")
st.metric("Tasa máxima de crecimiento", f"{max(dP_dt):.3f} m/día")

# 📊 Gráfica de crecimiento
fig, ax = plt.subplots()
ax.plot(t, P, color='#388e3c', linewidth=2)
ax.set_facecolor('#f1f8e9')
fig.patch.set_facecolor('#e8f5e9')
ax.set_xlabel("Tiempo (días)")
ax.set_ylabel("Tamaño de la planta (m)")
ax.set_title("🌱 Curva de crecimiento logístico")
ax.grid(True, linestyle='--', alpha=0.5)
st.pyplot(fig)

# 📋 Tabla de resultados
df = pd.DataFrame({
    "Día": t,
    "Tamaño (m)": P,
    "Tasa de crecimiento (m/día)": dP_dt
})
st.dataframe(df)

# 💾 Exportar CSV
buf = io.BytesIO()
df.to_csv(buf, index=False)
buf.seek(0)
st.download_button("📥 Descargar resultados en CSV", data=buf, file_name="crecimiento_planta.csv", mime="text/csv")

# 🧠 Interpretación visual
st.header("🧠 Interpretación")
if r_ajustada < 0.05:
    st.warning("🌤️ La tasa de crecimiento es baja. La planta crecerá lentamente.")
elif r_ajustada > 0.5:
    st.success("🌞 La planta crecerá rápidamente gracias a condiciones óptimas.")
else:
    st.info("🌿 La planta tendrá un crecimiento moderado y estable.")
