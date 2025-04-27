"""
Simple test script to verify that the loading animation works.
"""

import dash
from dash import dcc, html
import time

# Initialize the app
app = dash.Dash(__name__)

# Define the layout
app.layout = html.Div([
    html.H1("Simple Loading Animation Test"),
    
    # Button to trigger the loading
    html.Button("Load Data", id="load-button", n_clicks=0),
    
    # Simple loading component
    dcc.Loading(
        id="loading-test",
        type="default",
        color="#007bff",
        children=[
            html.Div(id="loading-output", style={"height": "300px", "marginTop": "50px"})
        ]
    )
])

# Define the callback
@app.callback(
    dash.Output("loading-output", "children"),
    dash.Input("load-button", "n_clicks")
)
def load_data(n_clicks):
    if n_clicks > 0:
        # Simulate a long-running operation
        time.sleep(3)
        return html.Div([
            html.H3("Data Loaded!"),
            html.P(f"Button clicked {n_clicks} times")
        ])
    return "Click the button to load data"

# Run the app
if __name__ == "__main__":
    app.run_server(debug=True)
