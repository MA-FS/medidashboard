"""
theme.py - Callbacks for theme settings like dark mode toggle.
"""

from dash import Input, Output, callback, ctx

@callback(
    Output("color-scheme-store", "data"),
    Input("dark-mode-toggle", "n_clicks"),
    Input("color-scheme-store", "data")
)
def toggle_dark_mode(n_clicks, current_scheme):
    """Toggle between light and dark mode."""
    # Default to light mode if no data
    if current_scheme is None:
        current_scheme = "light"
    
    # Only toggle if the button was clicked
    if ctx.triggered_id == "dark-mode-toggle" and n_clicks:
        # Toggle between light and dark
        return "dark" if current_scheme == "light" else "light"
    
    # Return current scheme if not triggered by button
    return current_scheme
