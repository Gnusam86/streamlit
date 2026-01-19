import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from sympy import sympify, lambdify, symbols, integrate

st.set_page_config(page_title="Simulador de Cálculo", layout="wide")

st.title("Visualizador de Integrales y Sumas de Riemann")

# Configuración en la barra lateral
with st.sidebar:
    st.header("Parámetros")
    formula = st.text_input("Función f(x):", value="x**2 + 2")
    rango = st.slider("Intervalo [a, b]", -10.0, 10.0, (0.0, 4.0))
    n_rects = st.slider("Número de rectángulos (n)", 1, 50, 10)
    tipo_suma = st.selectbox("Punto de evaluación", ["Izquierda", "Derecha", "Punto Medio"])

try:
    # 1. Preparación Matemática
    x_sym = symbols('x')
    f_sym = sympify(formula)
    f_num = lambdify(x_sym, f_sym, "numpy")
    
    a, b = rango
    dx = (b - a) / n_rects
    
    # 2. Cálculo de la Integral Exacta
    area_exacta = float(integrate(f_sym, (x_sym, a, b)))

    # 3. Cálculo de la Suma de Riemann
    if tipo_suma == "Izquierda":
        x_riemann = np.linspace(a, b - dx, n_rects)
    elif tipo_suma == "Derecha":
        x_riemann = np.linspace(a + dx, b, n_rects)
    else: # Punto Medio
        x_riemann = np.linspace(a + dx/2, b - dx/2, n_rects)
    
    y_riemann = f_num(x_riemann)
    suma_area = np.sum(y_riemann * dx)

    # 4. Visualización
    fig, ax = plt.subplots(figsize=(10, 5))
    
    # Curva suave
    x_plot = np.linspace(a - 1, b + 1, 400)
    ax.plot(x_plot, f_num(x_plot), 'r', lw=2, label=f"f(x) = {formula}")
    
    # Dibujar Rectángulos
    ax.bar(x_riemann, y_riemann, width=dx, align='center' if tipo_suma=="Punto Medio" else ('edge' if tipo_suma=="Izquierda" else 'edge'), 
           alpha=0.3, color='green', edgecolor='black', label=f'Suma de Riemann: {suma_area:.4f}')
    
    # Ajustar alineación de 'edge' para Derecha (Matplotlib por defecto usa borde izquierdo)
    if tipo_suma == "Derecha":
        for rect in ax.patches:
            rect.set_x(rect.get_x() - dx)

    ax.axhline(0, color='black', lw=1)
    ax.set_title(f"Aproximación del área bajo la curva")
    ax.legend()
    
    # Mostrar resultados en Streamlit
    st.pyplot(fig)
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Área Exacta (Cálculo)", f"{area_exacta:.4f}")
    col2.metric("Suma de Riemann", f"{suma_area:.4f}")
    col3.metric("Error", f"{abs(area_exacta - suma_area):.4f}")

except Exception as e:
    st.error(f"Error: {e}. Revisa que la función sea válida para Python.")