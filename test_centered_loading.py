"""
Test script to verify that the centered loading animation works.
"""

import dash
from dash import dcc, html
import dash_bootstrap_components as dbc
import time

# Initialize the app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# Define the layout
app.layout = html.Div([
    html.H1("Centered Loading Animation Test", className="mb-4"),
    
    # Main content area
    html.Div([
        # Left sidebar (similar to the dashboard)
        html.Div([
            html.H4("Filters"),
            html.P("This is the sidebar area with filters.")
        ], style={"width": "25%", "padding": "20px", "backgroundColor": "#f8f9fa", "borderRight": "1px solid #dee2e6"}),
        
        # Main content area with loading animation
        html.Div([
            # Button to trigger the loading
            html.Div([
                html.H4("Biomarker Widgets"),
                html.Button("Load Data", id="load-button", n_clicks=0, 
                           style={"backgroundColor": "#28a745", "color": "white", "border": "none", "padding": "10px 20px", "borderRadius": "5px"})
            ], style={"display": "flex", "justifyContent": "space-between", "alignItems": "center", "marginBottom": "20px"}),
            
            # Loading component with the same structure as in the app
            html.Div([
                dcc.Loading(
                    id="loading-biomarkers",
                    type="circle",
                    color="#007bff",
                    children=[
                        html.Div(id="biomarker-widget-area")
                    ],
                    fullscreen=False,
                    className="loading-container"
                )
            ], style={"display": "flex", "justifyContent": "center", "alignItems": "center", "minHeight": "400px"})
        ], style={"width": "75%", "padding": "20px"})
    ], style={"display": "flex", "height": "calc(100vh - 100px)"})
])

# Add custom CSS for the loading animation
app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
        <style>
            /* Loading animation styling */
            .loading-container {
                min-height: 400px;
                width: 100%;
                position: relative;
                display: flex;
                align-items: center;
                justify-content: center;
            }
            
            /* Customize the Dash loading spinner */
            .dash-loading {
                position: absolute;
                top: 50%;
                left: 50%;
                transform: translate(-50%, -50%);
            }
            
            /* Ensure the loading spinner is centered */
            #loading-biomarkers {
                display: flex;
                align-items: center;
                justify-content: center;
                min-height: 50vh;
            }
            
            /* Apple-style loading animation */
            @keyframes pulse {
                0% { transform: scale(0.95); opacity: 0.7; }
                50% { transform: scale(1.05); opacity: 1; }
                100% { transform: scale(0.95); opacity: 0.7; }
            }
            
            /* Make the spinner larger and more visible */
            ._dash-loading-callback {
                font-size: 40px !important;
                color: #007bff !important;
                opacity: 0.9 !important;
                animation: pulse 1.5s infinite ease-in-out !important;
            }
            
            /* Add a subtle background to the loading area */
            .dash-loading-callback {
                background-color: rgba(255, 255, 255, 0.7) !important;
                backdrop-filter: blur(5px);
                border-radius: 16px;
                position: fixed !important;
                top: 50% !important;
                left: 50% !important;
                transform: translate(-50%, -50%) !important;
                z-index: 1000 !important;
                padding: 30px !important;
            }
        </style>
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
'''

# Define the callback
@app.callback(
    dash.Output("biomarker-widget-area", "children"),
    dash.Input("load-button", "n_clicks")
)
def load_data(n_clicks):
    if n_clicks > 0:
        # Simulate a long-running operation
        time.sleep(3)
        
        # Create a grid of cards to simulate biomarker widgets
        cards = []
        for i in range(6):
            card = html.Div([
                html.H5(f"Biomarker {i+1}"),
                html.P(f"Value: {(i+1) * 10}"),
                html.Div(style={"height": "100px", "backgroundColor": "#f8f9fa", "borderRadius": "5px"})
            ], style={"border": "1px solid #dee2e6", "borderRadius": "5px", "padding": "15px", "margin": "10px"})
            cards.append(card)
        
        return html.Div([
            html.Div(cards, style={"display": "grid", "gridTemplateColumns": "repeat(2, 1fr)", "gap": "20px"})
        ])
    
    return html.Div([
        html.P("Click the 'Load Data' button to load biomarker widgets.", 
              style={"textAlign": "center", "color": "#6c757d", "marginTop": "50px"})
    ])

# Run the app
if __name__ == "__main__":
    app.run_server(debug=True)
