"""
app.py - Main entry point for the MediDashboard application.
This module imports all components and sets up the app layout.
"""

# Import the app instance from app_instance.py
from .app_instance import app, server, theme

# Import database setup to ensure it's initialized
from . import database_setup

# Import layouts and components
from .layouts import dashboard_layout, settings_layout
from .components import navbar, biomarker_modal, add_reading_modal, view_readings_modal, delete_reading_confirm_modal, edit_reading_modal

# Import dash components
from dash import dcc, html, callback, Input, Output
import dash_mantine_components as dmc

# Set up the app layout with Mantine Provider
app.layout = dmc.MantineProvider(
    id="app-theme-provider",
    theme=theme,
    withGlobalClasses=True,
    children=[
        # Background logo removed

        dcc.Location(id='url', refresh=False),
        navbar,
        dmc.Container(
            id='page-content',
            fluid=True,
            px="md",
            py="md",
            style={
                "marginTop": "70px",  # Increased top margin for better spacing
                "animation": "fadeIn 0.4s ease-out"  # Add subtle animation
            },
            className="dashboard-content"
        ),
        add_reading_modal,  # Place modal outside page content so it can overlay
        view_readings_modal,  # Place view readings modal outside page content
        delete_reading_confirm_modal,  # Place delete confirmation modal outside page content
        edit_reading_modal,  # Place edit reading modal outside page content
        biomarker_modal,    # Place biomarker modal outside page content so it can overlay

        # Global stores for app state
        dcc.Store(id='dashboard-visible-biomarkers-store', storage_type='local', data="ALL"),  # Initialize with "ALL" to show all biomarkers by default
        dcc.Store(id='chart-time-range-store', storage_type='local', data='6m'),

        # Dark mode toggle store
        dcc.Store(id='color-scheme-store', storage_type='local', data='light'),
    ]
)

# Import callbacks to register them
from .callbacks import routing, dashboard, settings, biomarkers, readings, readings_management, edit_readings, theme

# Theme callback is now in callbacks/theme.py

# Run the app if this file is executed directly
if __name__ == '__main__':
    print("Starting MediDashboard server...")
    app.run(debug=True, host='127.0.0.1', port=8051)  # Using port 8051 to avoid conflicts
