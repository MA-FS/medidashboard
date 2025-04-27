"""
settings.py - Callbacks for the settings page.
"""

import os
import base64
import tempfile
import dash
import subprocess
import io
import pandas as pd
import traceback
from datetime import datetime
from dash import Input, Output, State, callback, html, dcc, ALL
import dash_bootstrap_components as dbc

from .. import bll
from ..utils import create_biomarker_table
from ..components import create_validation_summary, create_csv_preview_table, create_editable_csv_preview_table

@callback(
    Output("biomarker-table-container", "children"),
    Input("settings-tabs", "value"),
    Input("biomarker-update-trigger", "data") # Add trigger as input
)
def update_biomarker_table(active_tab, trigger):
    """Fetches biomarkers and updates the table when the Manage Biomarkers tab is active or trigger fires."""
    # Use ctx.triggered_id to optionally check which input fired if needed
    # For now, refresh if the tab is correct regardless of trigger
    if active_tab == "tab-manage-biomarkers":
        print(f"Refreshing biomarker table (Trigger: {trigger})") # Log refresh
        biomarkers = bll.get_all_biomarkers_grouped() # Fetch data using BLL
        return create_biomarker_table(biomarkers) # Generate table
    return "" # Return empty if other tab is active

@callback(
    Output("biomarker-modal", "is_open", allow_duplicate=True),
    Input("settings-tabs", "value"),
    prevent_initial_call='initial_duplicate'
)
def close_biomarker_modal_on_tab_switch(_):
    """Ensures the biomarker modal is closed when switching tabs."""
    # Always close the modal when switching tabs or when the page loads
    return False

# Database backup/restore functionality has been removed

@callback(
    Output("reference-range-container", "children"),
    Input("settings-tabs", "value"),
    Input("reference-range-update-trigger", "data")
)
def update_reference_range_container(active_tab, trigger):
    """Updates the reference range configuration UI when the Reference Ranges tab is active."""
    if active_tab != "tab-reference-ranges":
        return ""

    # Get all biomarkers and their reference ranges
    biomarkers = bll.get_all_biomarkers_grouped()

    # Create a form for each biomarker
    forms = []
    for biomarker in biomarkers:
        # Get reference range for this biomarker
        reference_range = bll.get_reference_range_for_biomarker(biomarker['id'])

        # Set default values
        range_type = reference_range.get('range_type', 'between') if reference_range else 'between'
        lower_bound = reference_range.get('lower_bound', None) if reference_range else None
        upper_bound = reference_range.get('upper_bound', None) if reference_range else None

        # Create form
        form = dbc.Form([
            dbc.Row([
                dbc.Col([
                    html.H5(f"{biomarker['name']} ({biomarker['unit']})")
                ], width=12)
            ], className="mb-2"),
            dbc.Row([
                dbc.Col([
                    dbc.Label("Range Type"),
                    dcc.Dropdown(
                        id={'type': 'range-type-dropdown', 'index': biomarker['id']},
                        options=[
                            {'label': 'Below', 'value': 'below'},
                            {'label': 'Above', 'value': 'above'},
                            {'label': 'Between', 'value': 'between'}
                        ],
                        value=range_type,
                        clearable=False
                    )
                ], width=4),
                dbc.Col([
                    dbc.Label("Lower Bound"),
                    dbc.Input(
                        id={'type': 'lower-bound-input', 'index': biomarker['id']},
                        type="number",
                        value=lower_bound,
                        disabled=range_type == 'below'
                    )
                ], width=3),
                dbc.Col([
                    dbc.Label("Upper Bound"),
                    dbc.Input(
                        id={'type': 'upper-bound-input', 'index': biomarker['id']},
                        type="number",
                        value=upper_bound,
                        disabled=range_type == 'above'
                    )
                ], width=3),
                dbc.Col([
                    html.Div(style={'height': '32px'}),  # Spacer to align button with inputs
                    dbc.Button(
                        "Save",
                        id={'type': 'save-range-button', 'index': biomarker['id']},
                        color="primary",
                        size="sm"
                    )
                ], width=2)
            ])
        ], className="mb-4")

        forms.append(form)

    # If no biomarkers, show a message
    if not forms:
        return dbc.Alert("No biomarkers defined yet. Add biomarkers first.", color="info")

    return html.Div(forms)

@callback(
    Output({'type': 'lower-bound-input', 'index': dash.ALL}, 'disabled'),
    Output({'type': 'upper-bound-input', 'index': dash.ALL}, 'disabled'),
    Input({'type': 'range-type-dropdown', 'index': dash.ALL}, 'value')
)
def update_range_inputs(range_types):
    """Enables/disables bound inputs based on the selected range type."""
    lower_disabled = [rt == 'below' for rt in range_types]
    upper_disabled = [rt == 'above' for rt in range_types]
    return lower_disabled, upper_disabled

@callback(
    Output("reference-range-update-trigger", "data"),
    Output("import-ranges-result", "children"),
    Input("import-australian-ranges-button", "n_clicks"),
    State("reference-range-update-trigger", "data"),
    prevent_initial_call=True
)
def import_australian_ranges(n_clicks, trigger_value):
    """Imports Australian reference ranges when the button is clicked."""
    if not n_clicks:
        return dash.no_update, dash.no_update

    try:
        # Run the import script
        script_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'import_australian_ranges.py')
        result = subprocess.run(['python', script_path], capture_output=True, text=True)

        if result.returncode == 0:
            # Success
            message = html.Div([
                html.H5("Import Successful", className="text-success"),
                html.Pre(result.stdout, style={"max-height": "200px", "overflow": "auto"})
            ])
            # Increment trigger to refresh the UI
            new_trigger = trigger_value + 1 if trigger_value is not None else 1
            return new_trigger, message
        else:
            # Error
            message = html.Div([
                html.H5("Import Failed", className="text-danger"),
                html.Pre(result.stderr, style={"max-height": "200px", "overflow": "auto"})
            ])
            return dash.no_update, message
    except Exception as e:
        # Exception
        message = html.Div([
            html.H5("Error", className="text-danger"),
            html.P(str(e))
        ])
        return dash.no_update, message

@callback(
    Output("reference-range-update-trigger", "data", allow_duplicate=True),
    Input({'type': 'save-range-button', 'index': dash.ALL}, 'n_clicks'),
    State({'type': 'range-type-dropdown', 'index': dash.ALL}, 'value'),
    State({'type': 'lower-bound-input', 'index': dash.ALL}, 'value'),
    State({'type': 'upper-bound-input', 'index': dash.ALL}, 'value'),
    State({'type': 'save-range-button', 'index': dash.ALL}, 'id'),
    State("reference-range-update-trigger", "data"),
    prevent_initial_call=True
)
def save_reference_range(n_clicks, range_types, lower_bounds, upper_bounds, button_ids, trigger_value):
    """Saves reference ranges when the save button is clicked."""
    # Find which button was clicked
    ctx = dash.callback_context
    if not ctx.triggered:
        return dash.no_update

    # Get the index of the clicked button
    button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    try:
        button_index = int(eval(button_id)['index'])
    except:
        return dash.no_update

    # Find the corresponding data in the arrays
    for i, bid in enumerate(button_ids):
        if bid['index'] == button_index:
            # Get the data for this biomarker
            range_type = range_types[i]
            lower_bound = lower_bounds[i]
            upper_bound = upper_bounds[i]

            # Save the reference range
            bll.update_reference_range_by_biomarker(button_index, range_type, lower_bound, upper_bound)

            # Increment trigger to refresh the UI
            new_trigger = trigger_value + 1 if trigger_value is not None else 1
            return new_trigger

    return dash.no_update

# Remove the initialization callback as it's causing issues

# Database backup functionality has been removed

# Export CSV button callback
@callback(
    Output("export-csv-download", "data"),
    Input("export-csv-button", "n_clicks"),
    prevent_initial_call=True
)
def handle_export_csv_button(n_clicks):
    """Exports all readings as CSV and triggers download when the export button is clicked."""
    if not n_clicks:
        return dash.no_update

    try:
        # Get CSV content
        csv_content = bll.export_readings_to_csv()

        # Return the CSV content for download
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"medidashboard_readings_{timestamp}.csv"

        return dict(
            content=csv_content,
            filename=filename
        )
    except Exception as e:
        print(f"Error exporting CSV: {str(e)}")
        return dash.no_update

# Store CSV content when uploaded
@callback(
    Output("csv-content-store", "data"),
    Input("upload-readings", "contents"),
    prevent_initial_call=True
)
def store_csv_content(contents):
    """Stores the CSV content when a file is uploaded."""
    if contents:
        return contents
    return dash.no_update

# Display filename when uploaded
@callback(
    Output("csv-filename-display", "children"),
    Output("validate-csv-button", "disabled"),
    Input("upload-readings", "filename"),
    prevent_initial_call=True
)
def update_filename_display(filename):
    """Updates the filename display and enables the validate button."""
    if filename:
        return html.Div([
            html.I(className="fas fa-file-csv me-2"),
            f"Selected file: {filename}"
        ], className="mt-2"), False
    return "", True

# Validate CSV when button clicked - Step 1: Show loading
@callback(
    Output("csv-validation-summary", "children"),
    Input("validate-csv-button", "n_clicks"),
    prevent_initial_call=True
)
def show_validation_loading(n_clicks):
    """Shows a loading message when validation starts."""
    if not n_clicks:
        return dash.no_update

    # Return loading message immediately to show progress
    return html.Div([
        dbc.Spinner(size="sm", color="primary", type="border", className="me-2"),
        "Validating CSV data..."
    ], className="d-flex align-items-center")

# Validate CSV when button clicked - Step 2: Perform validation
@callback(
    Output("csv-validation-summary", "children", allow_duplicate=True),
    Output("csv-preview-table", "children"),
    Output("csv-preview-collapse", "is_open"),
    Output("import-csv-button", "disabled"),
    Output("revalidate-csv-button", "style"),
    Input("validate-csv-button", "n_clicks"),
    State("csv-content-store", "data"),
    State("show-all-rows-switch", "value"),
    prevent_initial_call=True
)
def validate_csv_data(n_clicks, contents, show_all_rows):
    """Validates the CSV data and shows a preview."""
    if not n_clicks or not contents:
        return dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update

    try:
        # Decode the uploaded file with multiple encoding support
        decoded = bll.decode_csv_content(contents)

        # Validate the CSV content with the show_all_rows option
        validation_results = bll.validate_csv_content(decoded, show_all_rows=show_all_rows)

        # Create validation summary
        summary = create_validation_summary(validation_results)

        # Create preview table - use editable table if there are invalid rows
        if validation_results['invalid_rows'] > 0:
            preview_table = create_editable_csv_preview_table(
                validation_results['preview_data'],
                validation_results['row_results'][:len(validation_results['preview_data'])]
            )
            # Show revalidate button
            revalidate_button_style = {'display': 'inline-block'}
        else:
            preview_table = create_csv_preview_table(
                validation_results['preview_data'],
                validation_results['row_results'][:len(validation_results['preview_data'])]
            )
            # Hide revalidate button
            revalidate_button_style = {'display': 'none'}

        # Enable import button only if validation passed
        import_disabled = not validation_results['is_valid']

        return summary, preview_table, True, import_disabled, revalidate_button_style

    except Exception as e:
        error_div = html.Div([
            html.H5("Error", className="text-danger"),
            html.P(f"An error occurred during validation: {str(e)}")
        ])
        return error_div, dash.no_update, False, True, {'display': 'none'}

# Import CSV when button clicked - Step 1: Show loading
@callback(
    Output('output-readings-upload', 'children'),
    Input("import-csv-button", "n_clicks"),
    prevent_initial_call=True
)
def show_import_loading(n_clicks):
    """Shows a loading message when import starts."""
    if not n_clicks:
        return dash.no_update

    # Return loading message immediately to show progress
    return html.Div([
        dbc.Spinner(size="sm", color="primary", type="border", className="me-2"),
        "Importing CSV data..."
    ], className="d-flex align-items-center")

# Import CSV when button clicked - Step 2: Perform import
@callback(
    Output('output-readings-upload', 'children', allow_duplicate=True),
    Output('reading-update-trigger', 'data', allow_duplicate=True),
    Input("import-csv-button", "n_clicks"),
    State("csv-content-store", "data"),
    State('reading-update-trigger', 'data'),
    State("skip-duplicates-switch", "value"),
    prevent_initial_call=True
)
def import_csv_data(n_clicks, contents, trigger_value, skip_duplicates):
    """Imports the CSV data after validation."""
    print(f"Import CSV callback triggered. n_clicks: {n_clicks}, contents available: {contents is not None}, skip_duplicates: {skip_duplicates}")

    if not n_clicks or not contents:
        print("No clicks or no contents, returning no update")
        return dash.no_update, dash.no_update

    try:
        # Decode the uploaded file with multiple encoding support
        print(f"Decoding CSV content...")
        decoded = bll.decode_csv_content(contents)
        print(f"CSV content decoded successfully. First 100 chars: {decoded[:100]}")

        # Import readings from the CSV content
        print(f"Calling import_readings_from_csv with skip_duplicates={skip_duplicates}...")
        result = bll.import_readings_from_csv(decoded, skip_duplicates=skip_duplicates)
        print(f"Import result: success={result['success']}, imported={result.get('imported_count', 0)}, errors={result.get('error_count', 0)}, skipped={result.get('skipped_count', 0)}")

        if result['success']:
            # Create a success message with details
            message = html.Div([
                html.H5('Import Successful', className='text-success'),
                html.P(result['message']),
                html.P(f"Total rows: {result['total_rows']}"),
                html.P(f"Successfully imported: {result['imported_count']}"),
                html.P(f"Errors: {result['error_count']}"),
                html.P(f"Duplicates skipped: {result['skipped_count']}")
            ])

            # If there were errors, show them in a collapsible section
            if result['error_count'] > 0:
                error_list = html.Ul([html.Li(error) for error in result['errors']])
                message.children.append(html.Details([
                    html.Summary('Show Errors'),
                    error_list
                ]))

            # Increment the trigger to refresh the dashboard
            new_trigger_value = trigger_value + 1 if trigger_value is not None else 1
            print(f"Import successful, incrementing trigger from {trigger_value} to {new_trigger_value}")
            print(f"Imported {result['imported_count']} readings. This should trigger a dashboard refresh.")

            # Make sure we're returning the correct types
            if not isinstance(new_trigger_value, int):
                print(f"Warning: new_trigger_value is not an integer: {type(new_trigger_value)}")
                new_trigger_value = 1

            return message, new_trigger_value
        else:
            # Create an error message
            message = html.Div([
                html.H5('Import Failed', className='text-danger'),
                html.P(result['message'])
            ])

            # If there are specific errors, show them
            if result['errors']:
                error_list = html.Ul([html.Li(error) for error in result['errors']])
                message.children.append(html.Details([
                    html.Summary('Show Errors'),
                    error_list
                ]))

            print(f"Import failed: {result['message']}")
            return message, dash.no_update
    except Exception as e:
        print(f"Exception during import: {str(e)}")
        import traceback
        traceback.print_exc()
        return html.Div([
            html.H5('Error Processing File', className='text-danger'),
            html.P(str(e))
        ]), dash.no_update

# Download CSV template
@callback(
    Output("download-csv-template-data", "data"),
    Input("download-csv-template", "n_clicks"),
    prevent_initial_call=True
)
def download_csv_template(n_clicks):
    """Provides a template CSV file for download."""
    if not n_clicks:
        return dash.no_update

    # Create a template CSV with example data
    template_data = """Biomarker Name,Date,Time,Value,Unit
# Lipid Profile (lines starting with # are comments and will be ignored)
HDL Cholesterol,2023-01-01,08:00,1.5,mmol/L
LDL Cholesterol,2023-01-01,08:00,2.5,mmol/L
# Blood Sugar Levels
Glucose,2023-01-01,08:00,5.0,mmol/L
# Example of how to add more biomarkers
# Make sure your biomarker names match exactly with those in the system
# IMPORTANT: Date must be in YYYY-MM-DD format (e.g., 2023-01-01)
# IMPORTANT: Time must be in HH:MM format (e.g., 08:00)
# The complete format should be: Biomarker Name,YYYY-MM-DD,HH:MM,Value,Unit
"""

    return dict(content=template_data, filename="biomarker_template.csv")

# Revalidate CSV when button clicked
@callback(
    Output("csv-content-store", "data", allow_duplicate=True),
    Output("csv-validation-summary", "children", allow_duplicate=True),
    Output("csv-preview-table", "children", allow_duplicate=True),
    Output("csv-preview-collapse", "is_open", allow_duplicate=True),
    Output("import-csv-button", "disabled", allow_duplicate=True),
    Output("revalidate-csv-button", "style", allow_duplicate=True),
    Input("revalidate-csv-button", "n_clicks"),
    State("csv-content-store", "data"),
    State({"type": "csv-edit-input", "index": ALL, "column": ALL}, "value"),
    State({"type": "csv-edit-input", "index": ALL, "column": ALL}, "id"),
    State("show-all-rows-switch", "value"),
    prevent_initial_call=True
)
def revalidate_csv_data(n_clicks, contents, input_values, input_ids, show_all_rows):
    """Revalidates the CSV data after editing."""
    if not n_clicks or not contents:
        return dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update

    try:
        # Decode the uploaded file with multiple encoding support
        decoded = bll.decode_csv_content(contents)

        # Parse the CSV content
        df = pd.read_csv(io.StringIO(decoded), comment='#', skip_blank_lines=True)

        # Update the dataframe with the edited values
        for i, input_id in enumerate(input_ids):
            row_index = input_id["index"]
            column = input_id["column"].replace("_", " ")
            value = input_values[i]
            df.at[row_index, column] = value

        # Convert the dataframe back to CSV
        updated_csv = df.to_csv(index=False)

        # Create a new base64 encoded content
        updated_content = f"data:text/csv;base64,{base64.b64encode(updated_csv.encode('utf-8')).decode('utf-8')}"

        # Validate the updated CSV content with the show_all_rows option
        validation_results = bll.validate_csv_content(updated_csv, show_all_rows=show_all_rows)

        # Create validation summary
        summary = create_validation_summary(validation_results)

        # Create preview table - use editable table if there are invalid rows
        if validation_results['invalid_rows'] > 0:
            preview_table = create_editable_csv_preview_table(
                validation_results['preview_data'],
                validation_results['row_results'][:len(validation_results['preview_data'])]
            )
            # Show revalidate button
            revalidate_button_style = {'display': 'inline-block'}
        else:
            preview_table = create_csv_preview_table(
                validation_results['preview_data'],
                validation_results['row_results'][:len(validation_results['preview_data'])]
            )
            # Hide revalidate button
            revalidate_button_style = {'display': 'none'}

        # Enable import button only if validation passed
        import_disabled = not validation_results['is_valid']

        return updated_content, summary, preview_table, True, import_disabled, revalidate_button_style

    except Exception as e:
        print(f"Exception during revalidation: {str(e)}")
        import traceback
        traceback.print_exc()
        return dash.no_update, html.Div([
            html.H5("Error", className="text-danger"),
            html.P(f"An error occurred during revalidation: {str(e)}")
        ]), dash.no_update, True, True, {'display': 'none'}

# Delete row from CSV content
@callback(
    Output("csv-content-store", "data", allow_duplicate=True),
    Output("csv-validation-summary", "children", allow_duplicate=True),
    Output("csv-preview-table", "children", allow_duplicate=True),
    Output("csv-preview-collapse", "is_open", allow_duplicate=True),
    Output("import-csv-button", "disabled", allow_duplicate=True),
    Output("revalidate-csv-button", "style", allow_duplicate=True),
    Input({"type": "csv-delete-row", "index": ALL}, "n_clicks"),
    State("csv-content-store", "data"),
    State("show-all-rows-switch", "value"),
    prevent_initial_call=True
)
def delete_csv_row(n_clicks, contents, show_all_rows):
    """Deletes a row from the CSV content."""
    if not any(n_clicks) or not contents:
        return dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update

    # Find which button was clicked
    ctx = dash.callback_context
    if not ctx.triggered:
        return dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update

    # Get the index of the clicked button
    button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    try:
        row_index = int(eval(button_id)['index'])
    except:
        return dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update

    try:
        # Decode the uploaded file with multiple encoding support
        decoded = bll.decode_csv_content(contents)

        # Parse the CSV content
        df = pd.read_csv(io.StringIO(decoded), comment='#', skip_blank_lines=True)

        # Delete the row
        df = df.drop(row_index).reset_index(drop=True)

        # Convert the dataframe back to CSV
        updated_csv = df.to_csv(index=False)

        # Create a new base64 encoded content
        updated_content = f"data:text/csv;base64,{base64.b64encode(updated_csv.encode('utf-8')).decode('utf-8')}"

        # Validate the updated CSV content with the show_all_rows option
        validation_results = bll.validate_csv_content(updated_csv, show_all_rows=show_all_rows)

        # Create validation summary
        summary = create_validation_summary(validation_results)

        # Create preview table - use editable table if there are invalid rows
        if validation_results['invalid_rows'] > 0:
            preview_table = create_editable_csv_preview_table(
                validation_results['preview_data'],
                validation_results['row_results'][:len(validation_results['preview_data'])]
            )
            # Show revalidate button
            revalidate_button_style = {'display': 'inline-block'}
        else:
            preview_table = create_csv_preview_table(
                validation_results['preview_data'],
                validation_results['row_results'][:len(validation_results['preview_data'])]
            )
            # Hide revalidate button
            revalidate_button_style = {'display': 'none'}

        # Enable import button only if validation passed
        import_disabled = not validation_results['is_valid']

        return updated_content, summary, preview_table, True, import_disabled, revalidate_button_style

    except Exception as e:
        print(f"Exception during row deletion: {str(e)}")
        import traceback
        traceback.print_exc()
        return dash.no_update, html.Div([
            html.H5("Error", className="text-danger"),
            html.P(f"An error occurred during row deletion: {str(e)}")
        ]), dash.no_update, True, True, {'display': 'none'}
