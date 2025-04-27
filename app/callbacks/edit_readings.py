"""
edit_readings.py - Callbacks for editing biomarker readings.
"""

from dash import callback, Input, Output, State, ctx, no_update, ALL
import json
import dash_bootstrap_components as dbc
from dash.exceptions import PreventUpdate
from datetime import datetime

from app.components import create_readings_table
import app.bll as bll

# --- Edit Reading Modal Callbacks ---

@callback(
    Output("edit-reading-modal", "opened"),
    Output("edit-reading-id-store", "data"),
    Output("edit-reading-biomarker-id-store", "data"),
    Output("edit-reading-biomarker-unit-store", "data"),
    Output("edit-reading-date-picker", "date"),
    Output("edit-reading-time-picker", "value"),
    Output("edit-reading-value-input", "value"),
    Output("edit-reading-unit-display", "children"),
    Output("edit-reading-error-message", "children"),
    Input({"type": "edit-reading-button", "index": ALL}, "n_clicks"),
    Input("edit-reading-save-button", "n_clicks"),
    Input("edit-reading-cancel-button", "n_clicks"),
    State("edit-reading-modal", "opened"),
    State("view-readings-biomarker-id-store", "data"),
    prevent_initial_call=True
)
def toggle_edit_reading_modal(edit_clicks, save_clicks, cancel_clicks, is_open, current_biomarker_id):
    """Opens/closes the Edit Reading modal and loads reading data."""
    # Check if any trigger exists
    if not ctx.triggered:
        raise PreventUpdate

    # Get the trigger information
    trigger = ctx.triggered[0]
    triggered_id = ctx.triggered_id

    # Only proceed if the button was actually clicked (n_clicks > 0)
    if trigger['value'] is None or trigger['value'] <= 0:
        return is_open, no_update, no_update, no_update, no_update, no_update, no_update, no_update, no_update

    # Handle the "Edit Reading" button click
    if isinstance(triggered_id, dict) and triggered_id.get('type') == 'edit-reading-button':
        reading_id = triggered_id.get('index')

        # Get reading details
        reading = bll.get_reading_details(reading_id)
        if not reading:
            # Handle error
            return is_open, no_update, no_update, no_update, no_update, no_update, no_update, no_update, "Error: Reading not found"

        # Get biomarker details
        biomarker_id = reading['biomarker_id']
        biomarker = bll.get_biomarker_details(biomarker_id)
        if not biomarker:
            # Handle error
            return is_open, no_update, no_update, no_update, no_update, no_update, no_update, no_update, "Error: Biomarker not found"

        # Parse timestamp
        try:
            dt = datetime.fromisoformat(reading['timestamp'])
            date_value = dt.strftime("%Y-%m-%d")
            time_value = dt.strftime("%H:%M")
        except ValueError:
            # Handle error
            return is_open, no_update, no_update, no_update, no_update, no_update, no_update, no_update, "Error: Invalid timestamp format"

        # Return values to populate the modal
        return True, reading_id, biomarker_id, biomarker['unit'], date_value, time_value, reading['value'], biomarker['unit'], ""

    # Handle the "Save" or "Cancel" button click
    elif triggered_id in ["edit-reading-save-button", "edit-reading-cancel-button"]:
        return False, None, None, None, None, None, None, "Units", ""

    # Default: No change in modal state
    return is_open, no_update, no_update, no_update, no_update, no_update, no_update, no_update, no_update

@callback(
    Output("edit-reading-datetime-combined", "data"),
    Input("edit-reading-date-picker", "date"),
    Input("edit-reading-time-picker", "value"),
    prevent_initial_call=True
)
def update_edit_reading_datetime(date_value, time_value):
    """Combines date and time values into a single datetime string."""
    if not date_value or not time_value:
        return None

    # Combine date and time
    datetime_str = f"{date_value} {time_value}:00"
    return datetime_str

@callback(
    Output("edit-reading-error-message", "children", allow_duplicate=True),
    Output("view-readings-table-container", "children", allow_duplicate=True),
    Output("reading-update-trigger", "data", allow_duplicate=True),
    Input("edit-reading-save-button", "n_clicks"),
    State("edit-reading-id-store", "data"),
    State("edit-reading-datetime-combined", "data"),
    State("edit-reading-date-picker", "date"),
    State("edit-reading-time-picker", "value"),
    State("edit-reading-value-input", "value"),
    State("view-readings-biomarker-id-store", "data"),
    State("edit-reading-biomarker-unit-store", "data"),
    State("reading-update-trigger", "data"),
    prevent_initial_call=True
)
def save_edited_reading(n_clicks, reading_id, datetime_combined, date_value, time_value, value, biomarker_id, biomarker_unit, trigger_value):
    """Handles saving an edited biomarker reading."""
    # Check if the save button was actually clicked
    if not n_clicks or n_clicks <= 0:
        raise PreventUpdate

    # Validation
    if not reading_id:
        return "Error: No reading ID provided", no_update, no_update

    if not date_value:
        return "Please select a date", no_update, no_update

    if not time_value:
        return "Please select a time", no_update, no_update

    if value is None:
        return "Please enter a value", no_update, no_update

    # Use the combined datetime from our pickers
    timestamp_str = None
    if datetime_combined:
        timestamp_str = datetime_combined
    # Construct from individual date and time components if needed
    elif date_value and time_value:
        try:
            timestamp_str = f"{date_value} {time_value}:00"
            # Validate the timestamp by parsing it
            datetime.fromisoformat(timestamp_str)
        except ValueError:
            return "Invalid date/time format", no_update, no_update

    if not timestamp_str:
        return "Invalid date/time format", no_update, no_update

    # Convert the value to string
    value_str = str(value) if value is not None else ""

    # Update the reading
    try:
        result, error = bll.update_existing_reading(reading_id, timestamp_str, value_str)

        if not result:
            return error, no_update, no_update
        else:
            # If successful, refresh the readings table
            biomarker = bll.get_biomarker_details(biomarker_id)
            readings = bll.get_readings_for_display(biomarker_id)
            table = create_readings_table(readings, biomarker_unit)

            # Increment the trigger to refresh the dashboard
            new_trigger_value = trigger_value + 1 if trigger_value is not None else 1

            return "", table, new_trigger_value
    except Exception as e:
        print(f"Error updating reading: {str(e)}")
        return f"Error updating reading: {str(e)}", no_update, no_update
