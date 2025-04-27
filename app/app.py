"""
app.py - Main entry point for the MediDashboard application.
This module imports all components and sets up the app layout.
"""

# Import the app instance from app_instance.py
from .app_instance import app, server

# Import database setup to ensure it's initialized
from . import database_setup

# Import layouts and components
from .layouts import dashboard_layout, settings_layout
from .components import navbar, biomarker_modal, add_reading_modal, view_readings_modal, delete_reading_confirm_modal, edit_reading_modal

# Import dash components
from dash import dcc, html

# Set up the app layout
app.layout = html.Div([
    # Background logo that stays fixed as user scrolls - using inline HTML
    html.Div([
        html.Iframe(
            srcDoc='''
            <html>
            <body style="margin:0; overflow:hidden;">
                <img src="/assets/logo.png" style="
                    position: fixed;
                    top: 50%;
                    left: 50%;
                    transform: translate(-50%, -50%);
                    width: 80vh;
                    height: 80vh;
                    opacity: 0.7;
                    pointer-events: none;
                    object-fit: contain;
                ">
            </body>
            </html>
            ''',
            style={
                'position': 'fixed',
                'top': '0',
                'left': '0',
                'width': '100%',
                'height': '100%',
                'border': 'none',
                'zIndex': '-1',
                'pointerEvents': 'none',
            },
            id='background-logo-frame'
        )
    ], id='background-logo-container'),

    dcc.Location(id='url', refresh=False),
    navbar,
    html.Div(id='page-content', className="container-fluid"),
    add_reading_modal,  # Place modal outside page content so it can overlay
    view_readings_modal,  # Place view readings modal outside page content
    delete_reading_confirm_modal,  # Place delete confirmation modal outside page content
    edit_reading_modal,  # Place edit reading modal outside page content
    biomarker_modal,    # Place biomarker modal outside page content so it can overlay

    # Global stores for app state
    dcc.Store(id='dashboard-visible-biomarkers-store', storage_type='local', data="ALL"),  # Initialize with "ALL" to show all biomarkers by default
    dcc.Store(id='chart-time-range-store', storage_type='local', data='6m'),
])

# Import callbacks to register them
from .callbacks import routing, dashboard, settings, biomarkers, readings, readings_management, edit_readings

# Run the app if this file is executed directly
if __name__ == '__main__':
    print("Starting MediDashboard server...")
    app.run(debug=True, host='127.0.0.1', port=8051)  # Using port 8051 to avoid conflicts
