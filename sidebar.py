import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.graph_objects as go
import numpy as np
import math

# CSV-Dateien laden
df_gesamt_deutschland = pd.read_csv('data/1gesamt_deutschland.csv')
df_gesamt_deutschland_monthly = pd.read_csv('data/gesamt_deutschland_monthly.csv')
df_grouped = pd.read_csv('data/df_grouped.csv')
aggregated_df = pd.read_csv('data/aggregated_df.csv')
df_reduced = pd.read_csv('data/df_reduced.csv')

# Funktion zur Formatierung der Y-Achse für den monatlichen Graphen
def formatter(value):
    if value >= 1e9:
        return f'{value / 1e9:.0f} Mrd'
    elif value >= 1e6:
        return f'{value / 1e6:.0f} Mio'
    elif value >= 1e3:
        return f'{value / 1e3:.0f} K'
    else:
        return str(value)

# Dash-App erstellen
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server

# Kategorien und Subkategorien mit Links für zukünftige Navigation
def create_nav_structure():
    return {
        "Überblick über Deutschlands Handel": {
            "Gesamtüberblick seit 2008 bis 2024": {
                "Gesamter Export-, Import- und Handelsvolumen-Verlauf Deutschlands": "/gesamt-export-import-handelsvolumen"
            },
            "Überblick nach bestimmtem Jahr": {
                "Monatlicher Handelsverlauf": "/monatlicher-handelsverlauf",
                "Top 10 Handelspartner": ""/top-10-handelspartner"",
                "Länder mit größten Export- und Importzuwächsen (absolut)": "#",
                "Länder mit größten Export- und Importzuwächsen (relativ)": "#",
                "Top 10 Waren": "#",
                "Waren mit größten Export- und Importzuwächsen (absolut)": "#",
                "Waren mit größten Export- und Importzuwächsen (relativ)": "#"
            }
        },
        "Länderanalyse": {
            "Gesamtüberblick seit 2008 bis 2024": {
                "Gesamter Export-, Import- und Handelsvolumen-Verlauf mit Deutschland": "#",
                "Vergleich mit anderen Ländern": "#",
                "Export- und Importwachstumsrate": "#",
                "Platzierung im Export- und Importranking Deutschlands": "#",
                "Deutschlands Top 10 Waren im Handel": "#"
            },
            "Überblick nach bestimmtem Jahr": {
                "Handelsbilanz & Ranking": "#",
                "Monatlicher Handelsverlauf": "#",
                "Top 10 Export- und Importwaren": "#",
                "Top 4 Waren nach Differenz zum Vorjahr": "#",
                "Top 4 Waren nach Wachstum zum Vorjahr": "#"
            }
        },
        "Warenanalyse": {
            "Gesamtüberblick seit 2008 bis 2024": {
                "Gesamter Export- und Importverlauf der Ware": "#",
                "Deutschlands Top 5 Export- und Importländer der Ware": "#"
            }
        }
    }

categories = create_nav_structure()

def render_sidebar(categories):
    def create_items(subcategories):
        items = []
        for name, value in subcategories.items():
            if isinstance(value, dict):
                items.append(
                    dbc.AccordionItem(
                        dbc.Accordion(create_items(value), start_collapsed=True),
                        title=name
                    )
                )
            else:
                items.append(
                    html.Div(
                        html.A(name, href=value, style={"textDecoration": "none", "color": "black", "padding": "5px", "display": "block"})
                    )
                )
        return items
    
    return dbc.Accordion([
        dbc.AccordionItem(
            dbc.Accordion(create_items(subcategories), start_collapsed=True),
            title=category
        )
        for category, subcategories in categories.items()
    ], start_collapsed=True)

sidebar = html.Div([
    html.H2("Navigation", className="display-4"),
    html.Hr(),
    render_sidebar(categories)
], className="sidebar")

# Layout für die Dash-App
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),  # Location für URL-Überwachung
    dbc.Container([
        dbc.Row([
            dbc.Col(sidebar, width=3),
            dbc.Col(html.Div([
                html.H1("Graph wird hier angezeigt"),
                dcc.Dropdown(
                    id='jahr_dropdown',
                    options=[{'label': str(j), 'value': j} for j in sorted(df_gesamt_deutschland_monthly['Jahr'].unique())],
                    value=2024,  # Standardwert
                    clearable=False,
                    style={'width': '50%'}
                ),
                dcc.Graph(id='handel_graph')  # Der Graph wird hier angezeigt
            ]), width=9)
        ])
    ])


     # Hier wird der Codeblock für Subkategorie eingefügt
    html.Div(id='content', children=[
        html.H1("Top 10 Handelspartner Deutschlands"),
        dcc.Dropdown(
            id='jahr_dropdown_subkategorie',
            options=[{'label': str(j), 'value': j} for j in sorted(df_grouped['Jahr'].unique())],
            value=2024,  # Standardwert
            clearable=False,
            style={'width': '50%'}
        ),
        dcc.Graph(id='export_graph'),
        dcc.Graph(id='import_graph'),
        dcc.Graph(id='handelsvolumen_graph')
    ])
])


    
])

# Callback, um den Graphen für „Gesamter Export-, Import- und Handelsvolumen-Verlauf Deutschlands“ anzuzeigen
@app.callback(
    Output('handel_graph', 'figure'),
    [Input('url', 'pathname'), Input('jahr_dropdown', 'value')]
)
def update_graph(pathname, year_selected):
    if pathname == "/gesamt-export-import-handelsvolumen":
        fig = go.Figure()

        # Linien für Export, Import und Handelsvolumen
        for col, name, color in zip(
            ['gesamt_export', 'gesamt_import', 'gesamt_handelsvolumen'],
            ['Exportvolumen', 'Importvolumen', 'Gesamthandelsvolumen'],
            ['#1f77b4', '#ff7f0e', '#2ca02c']
        ):
            fig.add_trace(go.Scatter(
                x=df_gesamt_deutschland['Jahr'],
                y=df_gesamt_deutschland[col],
                mode='lines+markers',
                name=name,
                line=dict(width=2, color=color),
                hovertemplate=f'<b>{name}</b><br>Jahr: %{{x}}<br>Wert: %{{y:,.0f}} €<extra></extra>'
            ))

        # Berechnung der maximalen Y-Achse für Tick-Werte
        max_value = df_gesamt_deutschland[['gesamt_export', 'gesamt_import', 'gesamt_handelsvolumen']].values.max()
        tick_step = 500e9  # 500 Mrd als Schrittgröße
        tickvals = np.arange(0, max_value + tick_step, tick_step)

        # Layout-Anpassungen
        fig.update_layout(
            title='Entwicklung von Export, Import und Handelsvolumen',
            xaxis_title='Jahr',
            yaxis_title='Wert in €',
            yaxis=dict(
                tickformat=',',
                tickvals=tickvals,
                ticktext=[f"{val/1e9:.0f} Mrd" for val in tickvals]
            ),
            legend=dict(title='Kategorie', bgcolor='rgba(255,255,255,0.7)')
        )

        return fig

    # Callback für den monatlichen Handelsverlauf
    elif pathname == "/monatlicher-handelsverlauf":
        df_year_monthly = df_gesamt_deutschland_monthly[df_gesamt_deutschland_monthly['Jahr'] == year_selected]

        fig = go.Figure()

        for col, name, color in zip(
            ['export_wert', 'import_wert', 'handelsvolumen_wert'],
            ['Exportvolumen', 'Importvolumen', 'Gesamthandelsvolumen'],
            ['#1f77b4', '#ff7f0e', '#2ca02c']
        ):
            fig.add_trace(go.Scatter(
                x=df_year_monthly['Monat'],
                y=df_year_monthly[col],
                mode='lines+markers',
                name=name,
                line=dict(width=2, color=color),
                hovertemplate=f'<b>{name}</b><br>Monat: %{{x}}<br>Wert: %{{y:,.0f}} €<extra></extra>'
            ))

        # Maximale Werte bestimmen
        max_value = df_year_monthly[['export_wert', 'import_wert', 'handelsvolumen_wert']].values.max()

        # Auf nächste 50 Mrd aufrunden
        rounded_max = math.ceil(max_value / 50e9) * 50e9

        # Y-Achse in 25-Mrd-Schritten skalieren
        tickvals = np.arange(0, rounded_max + 1, 25e9)
        ticktext = [formatter(val) for val in tickvals]

        # Layout für den Graphen
        fig.update_layout(
            title=f'Monatlicher Export-, Import- und Handelsverlauf Deutschlands im Jahr {year_selected}',
            xaxis_title='Monat',
            yaxis_title='Wert in €',
            xaxis=dict(
                tickmode='array',
                tickvals=list(range(1, 13)),
                ticktext=['Jan', 'Feb', 'Mär', 'Apr', 'Mai', 'Jun', 'Jul', 'Aug', 'Sep', 'Okt', 'Nov', 'Dez']
            ),
            yaxis=dict(
                tickvals=tickvals,
                ticktext=ticktext
            ),
            legend=dict(title='Kategorie', bgcolor='rgba(255,255,255,0.7)')
        )

        return fig

    elif pathname == "/top-10-handelspartner":
    top_10_export = df_grouped[(df_grouped['export_ranking'] <= 10) & (df_grouped['Jahr'] == year_selected)][["Land", "export_wert"]]
    top_10_import = df_grouped[(df_grouped['import_ranking'] <= 10) & (df_grouped['Jahr'] == year_selected)][["Land", "import_wert"]]
    top_10_handelsvolumen = df_grouped[(df_grouped['handelsvolumen_ranking'] <= 10) & (df_grouped['Jahr'] == year_selected)][["Land", "handelsvolumen_wert"]]

    top_10_export = top_10_export.sort_values(by="export_wert", ascending=False)
    top_10_import = top_10_import.sort_values(by="import_wert", ascending=False)
    top_10_handelsvolumen = top_10_handelsvolumen.sort_values(by="handelsvolumen_wert", ascending=False)

    fig_export = go.Figure([go.Bar(
        x=top_10_export["Land"],
        y=top_10_export["export_wert"],
        text=[formatter(v) for v in top_10_export["export_wert"]],
        textposition='auto',
        marker=dict(color='blue')
    )])
    fig_export.update_layout(title="Top 10 Exportländer", xaxis_title="Land", yaxis_title="Exportwert in €")

    fig_import = go.Figure([go.Bar(
        x=top_10_import["Land"],
        y=top_10_import["import_wert"],
        text=[formatter(v) for v in top_10_import["import_wert"]],
        textposition='auto',
        marker=dict(color='orange')
    )])
    fig_import.update_layout(title="Top 10 Importländer", xaxis_title="Land", yaxis_title="Importwert in €")

    fig_handelsvolumen = go.Figure([go.Bar(
        x=top_10_handelsvolumen["Land"],
        y=top_10_handelsvolumen["handelsvolumen_wert"],
        text=[formatter(v) for v in top_10_handelsvolumen["handelsvolumen_wert"]],
        textposition='auto',
        marker=dict(color='green')
    )])
    fig_handelsvolumen.update_layout(title="Top 10 Handelsvolumen", xaxis_title="Land", yaxis_title="Handelsvolumen in €")

    return fig_export, fig_import, fig_handelsvolumen

    

    else:
        return {}  # Leeres Diagramm, wenn die URL nicht passt

if __name__ == "__main__":
    app.run_server(debug=True)
