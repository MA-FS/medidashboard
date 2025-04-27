"""
layouts.py - Page layouts for the MediDashboard application.
"""

from dash import dcc, html
import dash_bootstrap_components as dbc

# --- Dashboard Layout ---
dashboard_layout = dbc.Container(fluid=True, className="px-0 g-0", children=[
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    dbc.Row([
                        dbc.Col(
                            html.H4("Filter by Category", className="filter-title mb-0"),
                            width="auto"
                        ),
                        dbc.Col(
                            dbc.Button([
                                html.I(className="fas fa-plus me-2"),
                                "Add New Reading"
                            ],
                            id="add-reading-button",
                            color="success",
                            className="ms-auto add-reading-btn",
                            style={
                                "background": "linear-gradient(135deg, #28a745 0%, #20c997 100%)",
                                "boxShadow": "0 4px 10px rgba(40, 167, 69, 0.2)",
                                "border": "none",
                                "padding": "8px 16px",
                                "fontWeight": "500"
                            }),
                            width="auto"
                        ),
                    ], justify="between", align="center", className="mb-3"),
                    html.Div(
                        id='category-filter-buttons',
                        className="category-buttons-container mb-3"
                    ),
                    dcc.Store(id='selected-category-store', data='Lipid Profile'),
                    # Add other filters later if needed (e.g., date range)
                ])
            ], className="filter-card"),
        ], width=3, className="sticky-filter", style={"marginTop": "0"}),
        dbc.Col([
            # Simple loading component with biomarker widget area
            dcc.Loading(
                id="loading-biomarkers",
                type="default", # Use the default spinner which is more visible
                color="#007bff", # Apple blue color
                children=[
                    html.Div(id='biomarker-widget-area')
                ],
            ),
            dcc.Store(id='reading-update-trigger', data=0), # Trigger for reading updates
            # Note: The actual dashboard-visible-biomarkers-store is defined in app.py with storage_type='local'
            dcc.Store(id='chart-time-range-store', data='all') # Store for time range preference - 'all' shows all readings
        ], width=9),
    ], className="g-0")
])

# --- Settings Layout ---
settings_layout = dbc.Container(fluid=True, className="px-0 g-0", children=[
    html.H3("Settings"),
    # Use dcc.Tabs for callbacks triggered by tab activation
    dcc.Tabs(id="settings-tabs", value='tab-manage-biomarkers', children=[
        dcc.Tab(label="Manage Biomarkers", value="tab-manage-biomarkers", children=[
            dbc.Card(dbc.CardBody([
                html.H4("Defined Biomarkers", className="card-title"),
                html.Div(id="biomarker-table-container"),
                dbc.Button(
                    [html.I(className="fas fa-plus me-2"), "Add New Biomarker"],
                    id="add-biomarker-button",
                    color="primary",
                    className="mt-3 settings-btn-primary"
                ),
                dcc.Store(id='biomarker-update-trigger', data=0), # Trigger store for table refresh
                dcc.Store(id='biomarker-delete-id-store', data=None), # Store ID for delete confirmation
                dcc.ConfirmDialog(
                    id='confirm-biomarker-delete',
                    message='Are you sure you want to delete this biomarker and all its readings?',
                ),
            ]))
        ]),
        dcc.Tab(label="Reference Ranges", value="tab-reference-ranges", children=[
            dbc.Card(dbc.CardBody([
                html.H4("Configure Reference Ranges", className="card-title"),
                html.P("Set reference ranges for your biomarkers to visualize when values are within or outside normal ranges."),
                html.Div(id="reference-range-container"),
                dbc.Button(
                    [html.I(className="fas fa-download me-2"), "Import Australian Ranges"],
                    id="import-australian-ranges-button",
                    color="info",
                    className="mt-3 settings-btn-info"
                ),
                html.Div(id="import-ranges-result", className="mt-2"),
                dcc.Store(id='reference-range-update-trigger', data=0), # Trigger store for refresh
            ]))
        ]),
        dcc.Tab(label="Data Management", value="tab-data-management", children=[
            dbc.Card(dbc.CardBody([
                html.H4("Data Export & Import", className="card-title"),
                html.P("Export your biomarker data as CSV or import readings from a CSV file."),
                dbc.Button(
                    [html.I(className="fas fa-file-export me-2"), "Export Readings as CSV"],
                    id="export-csv-button",
                    color="info",
                    className="me-2 settings-btn-info"
                ),
                dcc.Download(id="export-csv-download"),

                html.Hr(),

                html.H4("Import Readings", className="card-title mt-4"),
                html.P("Import biomarker readings from a CSV file. The file should have the following columns:"),
                html.Ul([
                    html.Li("Biomarker Name - must match an existing biomarker name"),
                    html.Li("Date - in YYYY-MM-DD format"),
                    html.Li("Time - in HH:MM format (optional)"),
                    html.Li("Value - the reading value"),
                    html.Li("Unit - optional, helps match with existing biomarkers")
                ]),
                dbc.Alert([
                    html.I(className="fas fa-info-circle me-2"),
                    "Lines starting with # are treated as comments and will be ignored."
                ], color="info", className="mb-3"),

                # Store for CSV content
                dcc.Store(id="csv-content-store", storage_type="memory"),
                # Add reading-update-trigger to settings page as well
                dcc.Store(id='reading-update-trigger', data=0),

                # Step 1: Select CSV File
                dbc.Card([
                    dbc.CardHeader("Step 1: Select CSV File"),
                    dbc.CardBody([
                        dcc.Upload(
                            id='upload-readings',
                            children=html.Div([
                                html.I(className="fas fa-file-csv me-2"),
                                'Drag and Drop or ',
                                html.A('Select CSV File')
                            ]),
                            style={
                                'width': '100%',
                                'height': '60px',
                                'lineHeight': '60px',
                                'borderWidth': '1px',
                                'borderStyle': 'dashed',
                                'borderRadius': '5px',
                                'textAlign': 'center',
                                'margin': '10px 0'
                            },
                            multiple=False
                        ),
                        html.Div(id='csv-filename-display')
                    ])
                ], className="mb-3"),

                # Step 2: Validate CSV Data
                dbc.Card([
                    dbc.CardHeader("Step 2: Validate CSV Data"),
                    dbc.CardBody([
                        dbc.Row([
                            dbc.Col(
                                dbc.Button(
                                    [html.I(className="fas fa-check-circle me-2"), "Validate CSV"],
                                    id="validate-csv-button",
                                    color="primary",
                                    className="mb-3 px-4 py-2 settings-btn-primary",
                                    disabled=True
                                ),
                                width="auto"
                            ),
                            dbc.Col(
                                dbc.Button(
                                    [html.I(className="fas fa-sync me-2"), "Revalidate"],
                                    id="revalidate-csv-button",
                                    color="warning",
                                    className="mb-3 px-4 py-2 settings-btn-warning",
                                    style={'display': 'none'}
                                ),
                                width="auto"
                            ),
                            dbc.Col(
                                html.Div([
                                    dbc.Checkbox(
                                        id="show-all-rows-switch",
                                        label="Show all rows",
                                        value=False,
                                        className="mb-3 apple-switch"
                                    )
                                ], className="form-switch-container"),
                                width="auto",
                                className="d-flex align-items-center ms-3"
                            ),
                        ]),
                        html.Div(id="csv-validation-summary"),
                        dbc.Collapse([
                            html.H5("CSV Preview", className="mt-3"),
                            html.P("The table below shows a preview of your CSV data with validation status. You can edit rows with errors and then click Revalidate."),
                            html.Div(id="csv-preview-table", style={"maxHeight": "400px", "overflowY": "auto", "overflowX": "hidden"})
                        ], id="csv-preview-collapse", is_open=False)
                    ])
                ], className="mb-3"),

                # Step 3: Import Data
                dbc.Card([
                    dbc.CardHeader("Step 3: Import Data"),
                    dbc.CardBody([
                        dbc.Row([
                            dbc.Col(
                                dbc.Button(
                                    [html.I(className="fas fa-file-import me-2"), "Import Data"],
                                    id="import-csv-button",
                                    color="success",
                                    className="mb-3 settings-btn-success",
                                    disabled=True
                                ),
                                width="auto"
                            ),
                            dbc.Col(
                                html.Div([
                                    dbc.Checkbox(
                                        id="skip-duplicates-switch",
                                        label="Skip duplicates",
                                        value=True,
                                        className="mb-3 apple-switch"
                                    )
                                ], className="form-switch-container"),
                                width="auto",
                                className="d-flex align-items-center ms-3"
                            ),
                        ]),
                        html.Div(id='output-readings-upload')
                    ])
                ], className="mb-3"),

                # Download Template
                dbc.Card([
                    dbc.CardHeader("Need Help?"),
                    dbc.CardBody([
                        html.P("Download a template CSV file to get started:"),
                        dbc.Button(
                            [html.I(className="fas fa-file-download me-2"), "Download Template"],
                            id="download-csv-template",
                            color="info",
                            className="settings-btn-info"
                        ),
                        dcc.Download(id="download-csv-template-data")
                    ])
                ])
            ]))
        ]),
        # Add other settings tabs here if needed (e.g., Appearance, Formatting)
    ])
])

# --- 404 Layout ---
def get_404_layout(pathname):
    """Returns a 404 layout for unknown routes."""
    return dbc.Container(fluid=True, className="px-0 g-0", children=[
        html.Div([
            html.H1("404: Not found", className="text-danger"),
            html.Hr(),
            html.P(f"The pathname {pathname} was not recognised..."),
        ], className="p-5 bg-light rounded-3")
    ])
