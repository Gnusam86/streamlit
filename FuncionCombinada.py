import streamlit as st
import numpy as np
import plotly.graph_objects as go

st.set_page_config(page_title="Función combinada", layout="centered")
st.title("Visualizador de Función Combinada: Cuadrática + Senoidal")

x_min = st.number_input("Valor mínimo de x", value=-10.0)
x_max = st.number_input("Valor máximo de x", value=10.0)
x = np.linspace(x_min, x_max, 400)

st.subheader("Parámetros de la Función Cuadrática")
a = st.slider("Coeficiente a", min_value=-5.0, max_value=5.0, value=1.0)
b = st.slider("Coeficiente b", min_value=-10.0, max_value=10.0, value=0.0)
c = st.slider("Coeficiente c", min_value=-10.0, max_value=10.0, value=0.0)

y = a * x**2 +b * np.sin(c*x)
st.write(f"Función Combinada: {a}x² + {b} * sin({c}x)")

fig = go.Figure()
fig.add_trace(go.Scatter(x=x, y=y, mode='lines', name='Función Combinada'))
fig.update_layout(title="Gráfica de la Función Combinada", xaxis_title='x', yaxis_title='f(x)')
st.plotly_chart(fig, use_container_width=True)