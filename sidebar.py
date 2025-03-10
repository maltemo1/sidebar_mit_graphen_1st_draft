import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.graph_objects as go
import numpy as np

# CSV-Datei laden
df_gesamt_deutschland = pd.read_csv('data/1gesamt_deutschland.csv')

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
                "Monatlicher Handelsverlauf": "#",
                "Top 10 Handelspartner": "#",
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
                dcc.Graph(id='handel_graph')  # Der Graph wird hier angezeigt
            ]), width=9)
        ])
    ])
])

# Callback, um den Graphen anzuzeigen, basierend auf der URL
@app.callback(
    Output('handel_graph', 'figure'),
    [Input('url', 'pathname')]
)
def update_graph(pathname):
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
                hovertemplate=f'<b>{name}</b><br>Jahr: %{{x}}<br>Wert: %{{y:,.0f}} €'
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
    else:
        return {}  # Leeres Diagramm, wenn die URL nicht passt

if __name__ == "__main__":
    app.run_server(debug=True)
