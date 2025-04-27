"""
app_instance.py - Creates and exports the Dash app instance and server.
This module is imported by other modules that need access to the app instance.
"""

import dash
import dash_bootstrap_components as dbc

# Import and initialize the database
from . import database_setup
database_setup.initialize_database()

# Initialize Dash app with Bootstrap and Font Awesome
app = dash.Dash(
    __name__,
    suppress_callback_exceptions=True,
    external_stylesheets=[
        dbc.themes.BOOTSTRAP,
        "https://use.fontawesome.com/releases/v6.4.2/css/all.css"  # Font Awesome for icons
    ],
    prevent_initial_callbacks='initial_duplicate'
)

# Create server instance for WSGI
server = app.server
