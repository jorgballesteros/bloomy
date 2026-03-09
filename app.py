#!/usr/bin/env python3
"""
BLOOMY - Bloomberg-style Opportunity Monitor You
Dashboard de portfolio profesional con datos en tiempo real
v3.0 - Binance Aesthetic
"""

import dash
from dash import dcc, html, Input, Output, State
import plotly.graph_objs as go
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import dash_bootstrap_components as dbc
import json
import os

# Configuración cargada desde archivos JSON
def load_config():
    """Carga configuración desde archivos JSON"""
    config_dir = os.path.join(os.path.dirname(__file__), 'config')
    
    # Cargar posiciones
    positions_path = os.path.join(config_dir, 'positions.json')
    try:
        with open(positions_path, 'r', encoding='utf-8') as f:
            positions = json.load(f)
    except Exception as e:
        print(f"Error loading positions: {e}")
        positions = {}
    
    # Cargar oportunidades
    opportunities_path = os.path.join(config_dir, 'opportunities.json')
    try:
        with open(opportunities_path, 'r', encoding='utf-8') as f:
            opportunities = json.load(f)
    except Exception as e:
        print(f"Error loading opportunities: {e}")
        opportunities = []
    
    return positions, opportunities

POSITIONS, OPPORTUNITIES = load_config()

# Paleta Custom
COLORS = {
    'bg_primary': '#0B0E11',
    'bg_secondary': '#1E2329',
    'bg_card': '#181A20',
    'border': '#2B3139',
    'text_primary': '#EAECEF',
    'text_secondary': '#848E9C',
    'gold': '#51C4C8',  # Cyan
    'green': '#0ECB81',
    'red': '#F6465D',
    'green_glow': 'rgba(14, 203, 129, 0.1)',
    'red_glow': 'rgba(246, 70, 93, 0.1)'
}

# Inicializar app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.title = "bloomy"

# Estilos globales
CARD_STYLE = {
    'background-color': COLORS['bg_card'],
    'border': f"1px solid {COLORS['border']}",
    'border-radius': '8px',
    'margin-bottom': '10px',
    'padding': '12px',
    'transition': 'all 0.2s ease',
    'cursor': 'pointer'
}

HEADER_STYLE = {
    'color': COLORS['gold'],
    'font-family': '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif',
    'font-size': '28px',
    'margin': '15px 0 5px 0',
    'font-weight': '700',
    'letter-spacing': '-0.5px'
}

# Funciones auxiliares
def load_analysis():
    """Carga el análisis del último informe"""
    try:
        analysis_path = os.path.join(os.path.dirname(__file__), 'reports', 'analysis.json')
        with open(analysis_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading analysis: {e}")
        return {}

def fetch_stock_data(ticker, period='3mo'):
    """Obtiene datos históricos de una acción"""
    try:
        stock = yf.Ticker(ticker)
        df = stock.history(period=period)
        info = stock.info
        return df, info
    except Exception as e:
        print(f"Error fetching {ticker}: {e}")
        return pd.DataFrame(), {}

def calculate_rsi(df, period=14):
    """Calcula RSI"""
    if len(df) < period:
        return None
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi.iloc[-1] if not rsi.empty else None

def calculate_sma(df, period):
    """Calcula SMA"""
    if len(df) < period:
        return None
    return df['Close'].rolling(window=period).mean().iloc[-1]

def get_trend(df):
    """Determina tendencia técnica simple"""
    if len(df) < 20:
        return "N/A"
    sma20 = calculate_sma(df, 20)
    current = df['Close'].iloc[-1]
    if sma20 is None:
        return "N/A"
    if current > sma20 * 1.02:
        return "↗ Alcista"
    elif current < sma20 * 0.98:
        return "↘ Bajista"
    else:
        return "→ Lateral"

def format_large_number(num):
    """Formatea números grandes (Market Cap, Volume)"""
    if num >= 1e12:
        return f"${num/1e12:.2f}T"
    elif num >= 1e9:
        return f"${num/1e9:.2f}B"
    elif num >= 1e6:
        return f"${num/1e6:.2f}M"
    else:
        return f"${num:,.0f}"

def create_sparkline(df):
    """Crea mini gráfico de línea con gradiente"""
    if df.empty:
        return go.Figure()
    
    # Determinar color (verde si subió, rojo si bajó)
    color = COLORS['green'] if df['Close'].iloc[-1] >= df['Close'].iloc[0] else COLORS['red']
    fill_color = COLORS['green_glow'] if df['Close'].iloc[-1] >= df['Close'].iloc[0] else COLORS['red_glow']
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df.index[-30:],
        y=df['Close'][-30:],
        mode='lines',
        line=dict(color=color, width=2),
        fill='tozeroy',
        fillcolor=fill_color
    ))
    
    fig.update_layout(
        margin=dict(l=0, r=0, t=0, b=0),
        height=50,
        showlegend=False,
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )
    return fig

# Layout
app.layout = dbc.Container([
    # Header
    dbc.Row([
        dbc.Col([
            html.H1("bloomy", style=HEADER_STYLE),
            html.P("Portfolio Monitor", style={
                'color': COLORS['text_secondary'], 
                'font-size': '13px', 
                'font-family': '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
                'margin': '0'
            })
        ], width=8),
        dbc.Col([
            html.Div(id='last-update', style={
                'text-align': 'right', 
                'margin-top': '20px', 
                'color': COLORS['text_secondary'], 
                'font-size': '11px', 
                'font-family': '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif'
            })
        ], width=4)
    ]),
    
    html.Hr(style={'border-color': COLORS['border'], 'margin': '10px 0', 'opacity': '0.5'}),
    
    # Main content
    dbc.Row([
        # Panel izquierdo: Posiciones
        dbc.Col([
            html.Div([
                html.Span("POSITIONS", style={'color': COLORS['gold'], 'font-size': '12px', 'font-weight': '600', 'font-family': '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif', 'letter-spacing': '0.5px'})
            ], style={'margin-bottom': '12px'}),
            html.Div(id='positions-panel'),
            
            # Gráfico comparativo de posiciones
            html.Div([
                html.Div([
                    html.Span("PERFORMANCE", style={'color': COLORS['gold'], 'font-size': '11px', 'font-weight': '600', 'letter-spacing': '0.5px'})
                ], style={'margin-bottom': '8px'}),
                
                # Botones de período
                dbc.ButtonGroup([
                    dbc.Button("1M", id='period-1m', size='sm', style={'background-color': COLORS['bg_card'], 'color': COLORS['text_primary'], 'border': f"1px solid {COLORS['border']}", 'font-size': '9px', 'padding': '4px 8px'}),
                    dbc.Button("3M", id='period-3m', size='sm', style={'background-color': COLORS['bg_secondary'], 'color': COLORS['gold'], 'border': f"1px solid {COLORS['gold']}", 'font-size': '9px', 'padding': '4px 8px'}),
                    dbc.Button("6M", id='period-6m', size='sm', style={'background-color': COLORS['bg_card'], 'color': COLORS['text_primary'], 'border': f"1px solid {COLORS['border']}", 'font-size': '9px', 'padding': '4px 8px'}),
                    dbc.Button("YTD", id='period-ytd', size='sm', style={'background-color': COLORS['bg_card'], 'color': COLORS['text_primary'], 'border': f"1px solid {COLORS['border']}", 'font-size': '9px', 'padding': '4px 8px'}),
                    dbc.Button("1Y", id='period-1y', size='sm', style={'background-color': COLORS['bg_card'], 'color': COLORS['text_primary'], 'border': f"1px solid {COLORS['border']}", 'font-size': '9px', 'padding': '4px 8px'}),
                ], style={'margin-bottom': '8px', 'width': '100%'}),
                
                html.Div(id='performance-chart')
            ], style={'margin-top': '15px'})
        ], width=3, style={'padding-right': '10px'}),
        
        # Panel central: Gráficos
        dbc.Col([
            dcc.Tabs(id='chart-tabs', value='NBIS', children=[
                dcc.Tab(label='NBIS', value='NBIS', 
                    style={
                        'background-color': COLORS['bg_card'], 
                        'color': COLORS['text_secondary'], 
                        'border': f"1px solid {COLORS['border']}", 
                        'font-family': '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif', 
                        'font-size': '12px', 
                        'padding': '8px 16px',
                        'font-weight': '500'
                    }, 
                    selected_style={
                        'background-color': COLORS['bg_secondary'], 
                        'color': COLORS['gold'], 
                        'font-family': '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif', 
                        'font-size': '12px', 
                        'font-weight': '600',
                        'border-bottom': f"2px solid {COLORS['gold']}"
                    }),
                dcc.Tab(label='NVDA', value='NVDA', 
                    style={
                        'background-color': COLORS['bg_card'], 
                        'color': COLORS['text_secondary'], 
                        'border': f"1px solid {COLORS['border']}", 
                        'font-family': '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif', 
                        'font-size': '12px', 
                        'padding': '8px 16px',
                        'font-weight': '500'
                    }, 
                    selected_style={
                        'background-color': COLORS['bg_secondary'], 
                        'color': COLORS['gold'], 
                        'font-family': '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif', 
                        'font-size': '12px', 
                        'font-weight': '600',
                        'border-bottom': f"2px solid {COLORS['gold']}"
                    }),
                dcc.Tab(label='OKLO', value='OKLO', 
                    style={
                        'background-color': COLORS['bg_card'], 
                        'color': COLORS['text_secondary'], 
                        'border': f"1px solid {COLORS['border']}", 
                        'font-family': '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif', 
                        'font-size': '12px', 
                        'padding': '8px 16px',
                        'font-weight': '500'
                    }, 
                    selected_style={
                        'background-color': COLORS['bg_secondary'], 
                        'color': COLORS['gold'], 
                        'font-family': '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif', 
                        'font-size': '12px', 
                        'font-weight': '600',
                        'border-bottom': f"2px solid {COLORS['gold']}"
                    })
            ], style={'border-radius': '8px 8px 0 0'}),
            html.Div(id='chart-content', style={'margin-top': '10px', 'background-color': COLORS['bg_card'], 'border-radius': '8px', 'padding': '10px'})
        ], width=6),
        
        # Panel derecho: Oportunidades
        dbc.Col([
            html.Div([
                html.Span("WATCHLIST", style={'color': COLORS['gold'], 'font-size': '12px', 'font-weight': '600', 'font-family': '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif', 'letter-spacing': '0.5px'})
            ], style={'margin-bottom': '12px'}),
            html.Div(id='opportunities-panel', style={'max-height': '800px', 'overflow-y': 'auto'})
        ], width=3, style={'padding-left': '10px'})
    ]),
    
    # Auto-refresh
    dcc.Interval(id='interval-component', interval=60*1000, n_intervals=0),
    
    # Store para período seleccionado
    dcc.Store(id='selected-period', data='3mo')
    
], fluid=True, style={
    'background-color': COLORS['bg_primary'], 
    'color': COLORS['text_primary'], 
    'min-height': '100vh', 
    'padding': '15px', 
    'font-family': '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif'
})

# Callbacks
@app.callback(
    Output('positions-panel', 'children'),
    Input('interval-component', 'n_intervals')
)
def update_positions(n):
    """Actualiza panel de posiciones"""
    cards = []
    
    for ticker, position in POSITIONS.items():
        df, info = fetch_stock_data(ticker, period='1mo')
        
        if df.empty:
            continue
        
        current_price = df['Close'].iloc[-1]
        shares = position['shares']
        cost_basis = position['cost_basis']
        market_value = current_price * shares
        cost_value = cost_basis * shares
        pl = market_value - cost_value
        pl_pct = (pl / cost_value) * 100
        
        change_1d = ((df['Close'].iloc[-1] - df['Close'].iloc[-2]) / df['Close'].iloc[-2] * 100) if len(df) > 1 else 0
        
        pl_color = COLORS['green'] if pl >= 0 else COLORS['red']
        change_color = COLORS['green'] if change_1d >= 0 else COLORS['red']
        change_bg = COLORS['green_glow'] if change_1d >= 0 else COLORS['red_glow']
        
        # Market cap
        market_cap = info.get('marketCap', 0)
        market_cap_str = format_large_number(market_cap) if market_cap else 'N/A'
        
        card = html.Div([
            html.A(
                html.Div([
                    html.Div([
                        html.Span(ticker, style={'color': COLORS['text_primary'], 'font-weight': '600', 'font-size': '13px'}),
                        html.Span(f" {change_1d:+.2f}%", style={
                            'color': change_color, 
                            'font-size': '11px', 
                            'margin-left': '8px',
                            'background-color': change_bg,
                            'padding': '2px 6px',
                            'border-radius': '4px',
                            'font-weight': '500'
                        })
                    ], style={'display': 'flex', 'align-items': 'center', 'margin-bottom': '4px'}),
                    html.Div(f"${current_price:.2f}", style={'font-size': '18px', 'margin': '2px 0', 'color': COLORS['text_primary'], 'font-weight': '600'}),
                    html.Div(f"Cap: {market_cap_str}", style={'font-size': '10px', 'color': COLORS['text_secondary'], 'margin': '4px 0'}),
                ]),
                href=f"https://finance.yahoo.com/quote/{ticker}",
                target="_blank",
                style={'text-decoration': 'none'}
            ),
            dcc.Graph(figure=create_sparkline(df), config={'displayModeBar': False}, style={'margin': '8px 0'}),
            html.Div(style={'border-top': f"1px solid {COLORS['border']}", 'margin': '8px 0', 'opacity': '0.5'}),
            html.Div([
                html.Div([
                    html.Span("Position: ", style={'font-size': '10px', 'color': COLORS['text_secondary']}),
                    html.Span(f"{shares} @ ${cost_basis:.2f}", style={'font-size': '10px', 'color': COLORS['text_primary']})
                ]),
                html.Div([
                    html.Span("P/L: ", style={'font-size': '10px', 'color': COLORS['text_secondary']}),
                    html.Span(f"${pl:+,.0f} ({pl_pct:+.1f}%)", style={'color': pl_color, 'font-size': '11px', 'font-weight': '600'})
                ], style={'margin-top': '2px'})
            ])
        ], style=CARD_STYLE, className='position-card')
        
        cards.append(card)
    
    return cards

@app.callback(
    Output('chart-content', 'children'),
    Input('chart-tabs', 'value'),
    Input('interval-component', 'n_intervals')
)
def update_chart(ticker, n):
    """Actualiza gráfico principal"""
    df, info = fetch_stock_data(ticker, period='3mo')
    
    if df.empty:
        return html.P("No hay datos disponibles", style={'color': COLORS['text_secondary']})
    
    # Candlestick con gradiente
    candlestick = go.Figure(data=[go.Candlestick(
        x=df.index,
        open=df['Open'],
        high=df['High'],
        low=df['Low'],
        close=df['Close'],
        increasing_line_color=COLORS['green'],
        decreasing_line_color=COLORS['red'],
        increasing_fillcolor=COLORS['green'],
        decreasing_fillcolor=COLORS['red']
    )])
    
    # SMA 20 y 50
    sma20 = df['Close'].rolling(window=20).mean()
    sma50 = df['Close'].rolling(window=50).mean()
    
    candlestick.add_trace(go.Scatter(
        x=df.index, y=sma20, mode='lines', 
        line=dict(color=COLORS['gold'], width=1.5, dash='dot'),
        name='SMA 20'
    ))
    
    candlestick.add_trace(go.Scatter(
        x=df.index, y=sma50, mode='lines',
        line=dict(color='#6C5CE7', width=1.5, dash='dot'),
        name='SMA 50'
    ))
    
    candlestick.update_layout(
        height=280,
        margin=dict(l=50, r=20, t=30, b=20),
        paper_bgcolor=COLORS['bg_card'],
        plot_bgcolor=COLORS['bg_card'],
        font=dict(color=COLORS['text_primary'], family='-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif', size=10),
        xaxis=dict(gridcolor=COLORS['border'], gridwidth=0.5, showgrid=True),
        yaxis=dict(gridcolor=COLORS['border'], gridwidth=0.5, showgrid=True),
        title=dict(text=f"{ticker} - Price Action", font=dict(size=12, color=COLORS['text_primary'], weight=600)),
        showlegend=True,
        legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1, font=dict(size=9))
    )
    
    # RSI con zonas coloreadas
    rsi_values = df['Close'].rolling(14).apply(lambda x: calculate_rsi(pd.DataFrame({'Close': x})), raw=False)
    
    rsi_fig = go.Figure()
    
    # Zonas de sobrecompra/sobreventa
    rsi_fig.add_hrect(y0=70, y1=100, fillcolor=COLORS['red'], opacity=0.1, line_width=0)
    rsi_fig.add_hrect(y0=0, y1=30, fillcolor=COLORS['green'], opacity=0.1, line_width=0)
    
    rsi_fig.add_trace(go.Scatter(
        x=df.index, y=rsi_values, mode='lines', 
        line=dict(color=COLORS['gold'], width=2),
        fill='tozeroy',
        fillcolor='rgba(240, 185, 11, 0.1)',
        name='RSI'
    ))
    
    rsi_fig.add_hline(y=70, line_dash="dot", line_color=COLORS['red'], line_width=1)
    rsi_fig.add_hline(y=30, line_dash="dot", line_color=COLORS['green'], line_width=1)
    rsi_fig.add_hline(y=50, line_dash="dot", line_color=COLORS['text_secondary'], line_width=0.5, opacity=0.5)
    
    rsi_fig.update_layout(
        height=160,
        margin=dict(l=50, r=20, t=30, b=20),
        paper_bgcolor=COLORS['bg_card'],
        plot_bgcolor=COLORS['bg_card'],
        font=dict(color=COLORS['text_primary'], family='-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif', size=10),
        xaxis=dict(gridcolor=COLORS['border'], gridwidth=0.5, showgrid=True),
        yaxis=dict(gridcolor=COLORS['border'], gridwidth=0.5, showgrid=True, range=[0, 100]),
        title=dict(text="RSI (14)", font=dict(size=12, color=COLORS['text_primary'])),
        showlegend=False
    )
    
    # Volumen con gradiente
    volume_fig = go.Figure()
    colors = [COLORS['green'] if df['Close'].iloc[i] >= df['Open'].iloc[i] else COLORS['red'] for i in range(len(df))]
    volume_fig.add_trace(go.Bar(
        x=df.index, y=df['Volume'], 
        marker_color=colors, 
        name='Vol', 
        opacity=0.7
    ))
    
    volume_fig.update_layout(
        height=130,
        margin=dict(l=50, r=20, t=30, b=20),
        paper_bgcolor=COLORS['bg_card'],
        plot_bgcolor=COLORS['bg_card'],
        font=dict(color=COLORS['text_primary'], family='-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif', size=10),
        xaxis=dict(gridcolor=COLORS['border'], gridwidth=0.5, showgrid=True),
        yaxis=dict(gridcolor=COLORS['border'], gridwidth=0.5, showgrid=True),
        title=dict(text="Volume", font=dict(size=12, color=COLORS['text_primary'])),
        showlegend=False
    )
    
    # Cargar análisis
    analysis_data = load_analysis()
    analysis = analysis_data.get(ticker, {})
    
    # Panel de análisis
    analysis_panel = None
    if analysis:
        analysis_panel = html.Div([
            html.Div([
                html.Span("ÚLTIMO ANÁLISIS", style={
                    'color': COLORS['gold'], 
                    'font-size': '11px', 
                    'font-weight': '600',
                    'letter-spacing': '0.5px'
                }),
                html.Span(f" ({analysis_data.get('last_update', 'N/A')})", style={
                    'color': COLORS['text_secondary'],
                    'font-size': '9px',
                    'margin-left': '8px'
                })
            ], style={'margin-bottom': '10px'}),
            
            # Recomendación
            html.Div([
                html.Span("Recomendación: ", style={
                    'color': COLORS['text_secondary'],
                    'font-size': '11px'
                }),
                html.Span(analysis.get('recommendation', 'N/A'), style={
                    'color': COLORS['text_primary'],
                    'font-size': '11px',
                    'font-weight': '600'
                })
            ], style={'margin-bottom': '8px'}),
            
            # Key Points
            html.Div([
                html.Div("Puntos Clave:", style={
                    'color': COLORS['text_secondary'],
                    'font-size': '10px',
                    'margin-bottom': '4px'
                }),
                html.Ul([
                    html.Li(point, style={
                        'color': COLORS['text_primary'],
                        'font-size': '10px',
                        'margin': '2px 0'
                    }) for point in analysis.get('key_points', [])
                ], style={'margin': '0', 'padding-left': '20px'})
            ], style={'margin-bottom': '8px'}),
            
            # Alert Levels
            html.Div([
                html.Span("Niveles: ", style={
                    'color': COLORS['text_secondary'],
                    'font-size': '10px'
                }),
                html.Span(analysis.get('alert_levels', 'N/A'), style={
                    'color': COLORS['gold'],
                    'font-size': '10px',
                    'font-weight': '600'
                })
            ])
        ], style={
            'background-color': COLORS['bg_secondary'],
            'border': f"1px solid {COLORS['border']}",
            'border-radius': '8px',
            'padding': '12px',
            'margin-top': '10px'
        })
    
    return html.Div([
        dcc.Graph(figure=candlestick, config={'displayModeBar': False}),
        dcc.Graph(figure=rsi_fig, config={'displayModeBar': False}),
        dcc.Graph(figure=volume_fig, config={'displayModeBar': False}),
        analysis_panel if analysis_panel else html.Div()
    ])

@app.callback(
    Output('opportunities-panel', 'children'),
    Input('interval-component', 'n_intervals')
)
def update_opportunities(n):
    """Actualiza panel de oportunidades"""
    page_opps = OPPORTUNITIES  # Mostrar todas las oportunidades
    
    cards = []
    for opp in page_opps:
        ticker = opp['ticker']
        df, info = fetch_stock_data(ticker, period='1mo')
        
        if df.empty:
            continue
        
        current_price = df['Close'].iloc[-1]
        change_1d = ((df['Close'].iloc[-1] - df['Close'].iloc[-2]) / df['Close'].iloc[-2] * 100) if len(df) > 1 else 0
        rsi = calculate_rsi(df)
        trend = get_trend(df)
        
        # Máximo 52 semanas
        df_52w, _ = fetch_stock_data(ticker, period='1y')
        high_52w = df_52w['High'].max() if not df_52w.empty else current_price
        dist_from_high = ((current_price - high_52w) / high_52w * 100)
        
        change_color = COLORS['green'] if change_1d >= 0 else COLORS['red']
        change_bg = COLORS['green_glow'] if change_1d >= 0 else COLORS['red_glow']
        
        # Market cap
        market_cap = info.get('marketCap', 0)
        market_cap_str = format_large_number(market_cap) if market_cap else 'N/A'
        
        card = html.Div([
            html.A(
                html.Div([
                    html.Div([
                        html.Span(f"{ticker}", style={'color': COLORS['text_primary'], 'font-size': '11px', 'font-weight': '600'}),
                        html.Span(f" {change_1d:+.2f}%", style={
                            'color': change_color, 
                            'font-size': '9px',
                            'background-color': change_bg,
                            'padding': '1px 4px',
                            'border-radius': '2px',
                            'margin-left': '4px',
                            'font-weight': '500'
                        })
                    ], style={'display': 'flex', 'align-items': 'center', 'justify-content': 'space-between', 'margin-bottom': '2px'}),
                    html.Div(opp['sector'], style={'font-size': '8px', 'color': COLORS['text_secondary'], 'margin': '0 0 4px 0'}),
                    html.Div(f"${current_price:.2f}", style={'font-size': '13px', 'color': COLORS['text_primary'], 'margin': '2px 0', 'font-weight': '600'}),
                    html.Div([
                        html.Span("RSI ", style={'color': COLORS['text_secondary'], 'font-size': '8px'}),
                        html.Span(f"{rsi:.0f}" if rsi else "N/A", style={'color': COLORS['gold'], 'font-size': '8px', 'font-weight': '600'}),
                        html.Span(" • ", style={'color': COLORS['text_secondary'], 'font-size': '8px', 'margin': '0 2px'}),
                        html.Span(trend, style={'color': COLORS['text_primary'], 'font-size': '8px'})
                    ], style={'margin': '4px 0 0 0'})
                ]),
                href=f"https://finance.yahoo.com/quote/{ticker}",
                target="_blank",
                style={'text-decoration': 'none'}
            )
        ], style={
            'background-color': COLORS['bg_card'],
            'border': f"1px solid {COLORS['border']}",
            'border-radius': '6px',
            'padding': '8px',
            'transition': 'all 0.2s ease',
            'cursor': 'pointer',
            'height': '100%'
        }, className='opportunity-card')
        
        cards.append(card)
    
    # Organizar cards en grid 2 columnas
    rows = []
    for i in range(0, len(cards), 2):
        row_cards = cards[i:i+2]
        if len(row_cards) == 1:
            # Solo una tarjeta en la última fila
            row = dbc.Row([
                dbc.Col(row_cards[0], width=6),
            ], style={'margin-bottom': '6px'})
        else:
            # Dos tarjetas
            row = dbc.Row([
                dbc.Col(row_cards[0], width=6),
                dbc.Col(row_cards[1], width=6),
            ], style={'margin-bottom': '6px'})
        rows.append(row)
    
    return rows

@app.callback(
    Output('last-update', 'children'),
    Input('interval-component', 'n_intervals')
)
def update_timestamp(n):
    """Actualiza timestamp de última actualización"""
    return f"Last update: {datetime.now().strftime('%H:%M:%S')}"

@app.callback(
    [Output('selected-period', 'data'),
     Output('period-1m', 'style'),
     Output('period-3m', 'style'),
     Output('period-6m', 'style'),
     Output('period-ytd', 'style'),
     Output('period-1y', 'style')],
    [Input('period-1m', 'n_clicks'),
     Input('period-3m', 'n_clicks'),
     Input('period-6m', 'n_clicks'),
     Input('period-ytd', 'n_clicks'),
     Input('period-1y', 'n_clicks')],
    prevent_initial_call=True
)
def update_period(m1, m3, m6, ytd, y1):
    """Actualiza período seleccionado y estilos de botones"""
    ctx = dash.callback_context
    if not ctx.triggered:
        selected = 'period-3m'
    else:
        selected = ctx.triggered[0]['prop_id'].split('.')[0]
    
    period_map = {
        'period-1m': '1mo',
        'period-3m': '3mo',
        'period-6m': '6mo',
        'period-ytd': 'ytd',
        'period-1y': '1y'
    }
    
    # Estilos para botones
    base_style = {
        'background-color': COLORS['bg_card'],
        'color': COLORS['text_primary'],
        'border': f"1px solid {COLORS['border']}",
        'font-size': '9px',
        'padding': '4px 8px'
    }
    
    active_style = {
        'background-color': COLORS['bg_secondary'],
        'color': COLORS['gold'],
        'border': f"1px solid {COLORS['gold']}",
        'font-size': '9px',
        'padding': '4px 8px'
    }
    
    styles = {
        'period-1m': active_style if selected == 'period-1m' else base_style,
        'period-3m': active_style if selected == 'period-3m' else base_style,
        'period-6m': active_style if selected == 'period-6m' else base_style,
        'period-ytd': active_style if selected == 'period-ytd' else base_style,
        'period-1y': active_style if selected == 'period-1y' else base_style,
    }
    
    return (
        period_map.get(selected, '3mo'),
        styles['period-1m'],
        styles['period-3m'],
        styles['period-6m'],
        styles['period-ytd'],
        styles['period-1y']
    )

@app.callback(
    Output('performance-chart', 'children'),
    [Input('interval-component', 'n_intervals'),
     Input('selected-period', 'data')]
)
def update_performance_chart(n, period):
    """Genera gráfico comparativo de performance"""
    fig = go.Figure()
    
    colors_map = {
        'NBIS': COLORS['gold'],
        'NVDA': '#00D9FF',
        'OKLO': '#FF6B9D'
    }
    
    for ticker in POSITIONS.keys():
        df, _ = fetch_stock_data(ticker, period=period)
        
        if df.empty:
            continue
        
        # Calcular % change normalizado (día 0 = 0%)
        first_price = df['Close'].iloc[0]
        pct_change = ((df['Close'] - first_price) / first_price) * 100
        
        fig.add_trace(go.Scatter(
            x=df.index,
            y=pct_change,
            mode='lines',
            name=ticker,
            line=dict(color=colors_map.get(ticker, COLORS['text_primary']), width=2),
            hovertemplate=f'{ticker}: %{{y:.2f}}%<extra></extra>'
        ))
    
    # Línea de referencia 0%
    fig.add_hline(y=0, line_dash="dot", line_color=COLORS['text_secondary'], line_width=1, opacity=0.5)
    
    fig.update_layout(
        height=200,
        margin=dict(l=40, r=10, t=10, b=30),
        paper_bgcolor=COLORS['bg_card'],
        plot_bgcolor=COLORS['bg_card'],
        font=dict(color=COLORS['text_primary'], family='-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif', size=9),
        xaxis=dict(
            gridcolor=COLORS['border'], 
            gridwidth=0.5,
            showgrid=True
        ),
        yaxis=dict(
            gridcolor=COLORS['border'], 
            gridwidth=0.5,
            showgrid=True,
            title=dict(text='% Change', font=dict(size=9))
        ),
        showlegend=True,
        legend=dict(
            orientation='h',
            yanchor='bottom',
            y=1.02,
            xanchor='right',
            x=1,
            font=dict(size=9)
        ),
        hovermode='x unified'
    )
    
    return dcc.Graph(figure=fig, config={'displayModeBar': False})

if __name__ == '__main__':
    app.run(debug=False, host='127.0.0.1', port=8050)
