"""
routing.py - URL routing callbacks for the MediDashboard application.
"""

from dash import Input, Output, callback

from ..layouts import dashboard_layout, settings_layout, get_404_layout

@callback(
    Output('page-content', 'children'),
    Output('biomarker-modal', 'opened', allow_duplicate=True),
    [Input('url', 'pathname')],
    prevent_initial_call='initial_duplicate'
)
def display_page(pathname):
    """Routes to the appropriate page based on the URL pathname."""
    # Always ensure the modal is closed when navigating between pages
    if pathname == '/settings':
        return settings_layout, False
    elif pathname == '/':
        return dashboard_layout, False
    else:
        # Handle 404 or redirect to dashboard
        return get_404_layout(pathname), False
