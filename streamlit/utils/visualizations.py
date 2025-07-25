"""
Módulo de utilidades para visualizaciones
Funciones auxiliares para crear gráficos consistentes en la aplicación.
"""

import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from typing import List, Dict, Any, Optional

# Importar configuración de colores
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import COLORS

def create_metric_card(title: str, value: Any, delta: Optional[str] = None) -> Dict[str, Any]:
    """
    Crea datos para una tarjeta de métrica.
    
    Args:
        title: Título de la métrica
        value: Valor principal
        delta: Cambio respecto al período anterior
    
    Returns:
        Diccionario con los datos de la métrica
    """
    return {
        'title': title,
        'value': value,
        'delta': delta
    }

def create_distribution_chart(data: pd.DataFrame, 
                            x_col: str, 
                            y_col: str,
                            title: str = "Distribución",
                            chart_type: str = "bar") -> go.Figure:
    """
    Crea un gráfico de distribución (barras o pie).
    
    Args:
        data: DataFrame con los datos
        x_col: Columna para el eje X (o labels en pie)
        y_col: Columna para el eje Y (o values en pie)
        title: Título del gráfico
        chart_type: Tipo de gráfico ('bar' o 'pie')
    
    Returns:
        Figura de Plotly
    """
    if chart_type == "bar":
        fig = px.bar(data, x=x_col, y=y_col, title=title,
                    color=x_col, color_discrete_sequence=list(COLORS.values()))
    else:  # pie
        fig = px.pie(data, names=x_col, values=y_col, title=title,
                    color_discrete_sequence=list(COLORS.values()))
    
    fig.update_layout(showlegend=True, height=400)
    return fig

def create_timeline_chart(data: pd.DataFrame,
                         x_col: str,
                         y_cols: List[str],
                         title: str = "Timeline") -> go.Figure:
    """
    Crea un gráfico de línea temporal.
    
    Args:
        data: DataFrame con los datos
        x_col: Columna para el eje X (tiempo)
        y_cols: Lista de columnas para el eje Y
        title: Título del gráfico
    
    Returns:
        Figura de Plotly
    """
    fig = go.Figure()
    
    colors = list(COLORS.values())
    for i, col in enumerate(y_cols):
        fig.add_trace(go.Scatter(
            x=data[x_col],
            y=data[col],
            mode='lines+markers',
            name=col,
            line=dict(color=colors[i % len(colors)])
        ))
    
    fig.update_layout(
        title=title,
        xaxis_title=x_col,
        yaxis_title="Valores",
        hovermode='x unified',
        height=400
    )
    
    return fig

def create_gauge_chart(value: float,
                      title: str,
                      max_value: float = 100,
                      thresholds: List[float] = [50, 80]) -> go.Figure:
    """
    Crea un gráfico de gauge (velocímetro).
    
    Args:
        value: Valor actual
        title: Título del gauge
        max_value: Valor máximo
        thresholds: Umbrales para colores [verde->amarillo, amarillo->rojo]
    
    Returns:
        Figura de Plotly
    """
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=value,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': title},
        delta={'reference': thresholds[0]},
        gauge={
            'axis': {'range': [None, max_value]},
            'bar': {'color': "darkblue"},
            'steps': [
                {'range': [0, thresholds[0]], 'color': "lightgray"},
                {'range': [thresholds[0], thresholds[1]], 'color': "yellow"},
                {'range': [thresholds[1], max_value], 'color': "red"}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': thresholds[1]
            }
        }
    ))
    
    fig.update_layout(height=250)
    return fig

def create_heatmap(data: List[List[float]],
                  x_labels: List[str],
                  y_labels: List[str],
                  title: str = "Heatmap") -> go.Figure:
    """
    Crea un mapa de calor.
    
    Args:
        data: Matriz de valores
        x_labels: Etiquetas del eje X
        y_labels: Etiquetas del eje Y
        title: Título del gráfico
    
    Returns:
        Figura de Plotly
    """
    fig = go.Figure(data=go.Heatmap(
        z=data,
        x=x_labels,
        y=y_labels,
        colorscale='YlOrRd',
        text=data,
        texttemplate="%{text}",
        textfont={"size": 10},
        hovertemplate="%{y} - %{x}: %{z}<extra></extra>"
    ))
    
    fig.update_layout(
        title=title,
        xaxis_title="",
        yaxis_title="",
        height=400
    )
    
    return fig

def format_currency(value: float, currency: str = "₡") -> str:
    """
    Formatea un valor como moneda.
    
    Args:
        value: Valor numérico
        currency: Símbolo de moneda
    
    Returns:
        String formateado
    """
    return f"{currency}{value:,.2f}"

def format_percentage(value: float, decimals: int = 1) -> str:
    """
    Formatea un valor como porcentaje.
    
    Args:
        value: Valor entre 0 y 100
        decimals: Número de decimales
    
    Returns:
        String formateado
    """
    return f"{value:.{decimals}f}%"

# Estilos CSS para componentes personalizados
CUSTOM_CSS = """
<style>
    .metric-card {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid #1f77b4;
        margin: 10px 0;
    }
    
    .status-ok {
        color: #2ca02c;
        font-weight: bold;
    }
    
    .status-warning {
        color: #ff9800;
        font-weight: bold;
    }
    
    .status-error {
        color: #d62728;
        font-weight: bold;
    }
    
    .info-box {
        background-color: #e3f2fd;
        padding: 15px;
        border-radius: 5px;
        margin: 10px 0;
    }
</style>
"""