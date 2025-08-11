import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from typing import List, Dict, Any, Optional
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import COLORS

def create_metric_card(title: str, value: Any, delta: Optional[str] = None) -> Dict[str, Any]:
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
    if chart_type == "bar":
        fig = px.bar(data, x=x_col, y=y_col, title=title,
                    color=x_col, color_discrete_sequence=list(COLORS.values()))
    else:
        fig = px.pie(data, names=x_col, values=y_col, title=title,
                    color_discrete_sequence=list(COLORS.values()))
    
    fig.update_layout(showlegend=True, height=400)
    return fig

def create_timeline_chart(data: pd.DataFrame,
                         x_col: str,
                         y_cols: List[str],
                         title: str = "Timeline") -> go.Figure:

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
    return f"{currency}{value:,.2f}"

def format_percentage(value: float, decimals: int = 1) -> str:
    return f"{value:.{decimals}f}%"


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