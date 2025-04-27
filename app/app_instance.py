"""
app_instance.py - Creates and exports the Dash app instance and server.
This module is imported by other modules that need access to the app instance.
"""

import dash
import dash_mantine_components as dmc

# Import and initialize the database
from . import database_setup
database_setup.initialize_database()

# Set React version for compatibility
dash._dash_renderer._set_react_version('18.2.0')

# Initialize Dash app with Mantine and Font Awesome
app = dash.Dash(
    __name__,
    suppress_callback_exceptions=True,
    external_stylesheets=[
        "https://use.fontawesome.com/releases/v6.4.2/css/all.css"  # Font Awesome for icons
    ],
    prevent_initial_callbacks='initial_duplicate'
)

# Create server instance for WSGI
server = app.server

# Apple-style color palette for Mantine theme
apple_colors = {
    'blue': '#007AFF',       # Primary blue
    'green': '#34C759',      # Success green
    'orange': '#FF9500',     # Warning orange
    'red': '#FF3B30',        # Error/danger red
    'gray': '#8E8E93',       # Neutral gray
    'light_gray': '#E5E5EA', # Light gray for backgrounds
    'dark_gray': '#3A3A3C',  # Dark gray for text
    'background': '#F2F2F7', # Background color
}

# Define Mantine theme with Apple-style design
theme = {
    'colorScheme': 'light',
    'colors': {
        'primary': ['#F0F9FF', '#E0F2FE', '#BAE6FD', '#7DD3FC', '#38BDF8', '#0EA5E9', '#0284C7', '#0369A1', '#075985', '#0C4A6E'],
        'blue': ['#F0F9FF', '#E0F2FE', '#BAE6FD', '#7DD3FC', '#38BDF8', '#0EA5E9', '#0284C7', '#0369A1', '#075985', '#0C4A6E'],
        'green': ['#F0FDF4', '#DCFCE7', '#BBF7D0', '#86EFAC', '#4ADE80', '#22C55E', '#16A34A', '#15803D', '#166534', '#14532D'],
        'red': ['#FEF2F2', '#FEE2E2', '#FECACA', '#FCA5A5', '#F87171', '#EF4444', '#DC2626', '#B91C1C', '#991B1B', '#7F1D1D'],
        'orange': ['#FFF7ED', '#FFEDD5', '#FED7AA', '#FDBA74', '#FB923C', '#F97316', '#EA580C', '#C2410C', '#9A3412', '#7C2D12'],
    },
    'primaryColor': 'blue',
    'fontFamily': '-apple-system, BlinkMacSystemFont, "SF Pro Text", "SF Pro Display", "Helvetica Neue", Arial, sans-serif',
    'components': {
        'Button': {
            'styles': {
                'root': {
                    'borderRadius': '8px',
                    'fontWeight': 500,
                    'transition': 'all 0.2s ease',
                },
            },
        },
        'Card': {
            'styles': {
                'root': {
                    'borderRadius': '12px',
                    'boxShadow': '0 2px 8px rgba(0, 0, 0, 0.08)',
                    'transition': 'all 0.3s ease',
                    '&:hover': {
                        'boxShadow': '0 4px 12px rgba(0, 0, 0, 0.12)',
                        'transform': 'translateY(-2px)',
                    },
                },
            },
        },
        'Modal': {
            'styles': {
                'root': {
                    'borderRadius': '16px',
                },
                'header': {
                    'fontWeight': 600,
                },
            },
        },
    },
    'other': {
        'appShellHeaderHeight': 60,
        'appShellNavbarWidth': 250,
    },
}
