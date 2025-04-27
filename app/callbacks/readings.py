"""
readings.py - Callbacks for reading management.
"""

import dash
from dash import Input, Output, State, callback, ctx
from datetime import datetime

from .. import bll

@callback(
    Output("add-reading-modal", "is_open"),
    Output("modal-biomarker-dropdown", "value", allow_duplicate=True),
    Output("modal-datetime-input", "value", allow_duplicate=True),  # Keep for backward compatibility
    Output("modal-date-picker", "date", allow_duplicate=True),
    Output("modal-time-picker", "value", allow_duplicate=True),
    Output("modal-value-input", "value", allow_duplicate=True),
    Output("modal-unit-display", "children", allow_duplicate=True),
    Output("modal-error-message", "children", allow_duplicate=True),
    Input("add-reading-button", "n_clicks"),
    Input("modal-save-button", "n_clicks"),
    Input("modal-cancel-button", "n_clicks"),
    State("add-reading-modal", "is_open"),
    prevent_initial_call=True
)
def toggle_add_reading_modal(add_clicks, save_clicks, cancel_clicks, is_open):
    """Opens/closes the Add Reading modal."""
    # Check if any trigger exists
    if not ctx.triggered:
        return is_open, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update

    # Get the ID of the element that triggered the callback
    triggered_id = ctx.triggered_id

    # Handle the "Add New Reading" button click
    if triggered_id == "add-reading-button" and add_clicks and add_clicks > 0:
        # Clear fields and open
        now = datetime.now()
        current_date = now.strftime("%Y-%m-%d")
        current_time = now.strftime("%H:%M")
        datetime_str = now.strftime("%Y-%m-%d %H:%M:%S")
        return True, None, datetime_str, current_date, current_time, None, "Units", ""

    # Handle the "Save" or "Cancel" button click
    elif triggered_id in ["modal-save-button", "modal-cancel-button"]:
        # Clear fields and close
        return False, None, None, None, None, None, "Units", ""

    # Default: No change in modal state
    return is_open, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update

@callback(
    Output("modal-biomarker-dropdown", "options"),
    Input("add-reading-modal", "is_open"),
    prevent_initial_call=True
)
def populate_biomarker_dropdown(is_open):
    """Populates the biomarker dropdown only when the modal is opened."""
    if not is_open:
        # Don't waste DB query if modal is closed
        return dash.no_update

    biomarkers = bll.get_all_biomarkers_grouped()
    options = [
        {'label': f"{b['name']} ({b['unit']})" + (f" - {b['category']}" if b['category'] else ""), 'value': b['id']}
        for b in biomarkers
    ]
    return options

@callback(
    Output("modal-unit-display", "children", allow_duplicate=True),
    Input("modal-biomarker-dropdown", "value"),
    prevent_initial_call=True
)
def update_reading_modal_units(selected_biomarker_id):
    """Updates the unit display in the Add Reading modal based on selected biomarker."""
    if selected_biomarker_id is None:
        return "Units" # Default text

    biomarker = bll.get_biomarker_details(selected_biomarker_id)
    if biomarker and 'unit' in biomarker:
        return biomarker['unit']
    else:
        return "Error!" # Should not happen if dropdown is populated correctly

@callback(
    Output("modal-datetime-combined", "data"),
    Output("modal-datetime-input", "value", allow_duplicate=True),  # Update the hidden input for backward compatibility
    Input("modal-date-picker", "date"),
    Input("modal-time-picker", "value"),
    prevent_initial_call=True
)
def combine_date_and_time(date_value, time_value):
    """Combines the date and time values into a single datetime string."""
    # Check if we have both date and time values
    if not date_value or not time_value:
        return None, None

    try:
        # Combine date and time into a single datetime string
        datetime_str = f"{date_value} {time_value}:00"
        # Validate the datetime string by parsing it
        datetime.strptime(datetime_str, "%Y-%m-%d %H:%M:%S")
        return datetime_str, datetime_str
    except ValueError:
        # If there's an error parsing the datetime, return None
        print(f"Error combining date {date_value} and time {time_value}")
        return None, None

@callback(
    Output("modal-error-message", "children", allow_duplicate=True),
    Output("reading-update-trigger", "data"), # Now outputting to the trigger
    Input("modal-save-button", "n_clicks"),
    State("modal-biomarker-dropdown", "value"),
    State("modal-datetime-combined", "data"),
    State("modal-datetime-input", "value"),  # Include the hidden input for backward compatibility
    State("modal-date-picker", "date"),
    State("modal-time-picker", "value"),
    State("modal-value-input", "value"),
    State("reading-update-trigger", "data"), # Get current trigger value
    prevent_initial_call=True
)
def save_new_reading(n_clicks, biomarker_id, datetime_combined, datetime_input, date_value, time_value, value, trigger_value):
    """Handles saving a new biomarker reading with enhanced validation and triggers dashboard refresh."""
    # Check if the save button was actually clicked
    if not n_clicks or n_clicks <= 0:
        return "", dash.no_update # No trigger if button not clicked

    # Validation
    if not biomarker_id:
        return "Please select a biomarker", dash.no_update

    if not date_value:
        return "Please select a date", dash.no_update

    if not time_value:
        return "Please select a time", dash.no_update

    if value is None:
        return "Please enter a value", dash.no_update

    # Use the most reliable timestamp source
    timestamp_str = None

    # First try the combined datetime from our new pickers
    if datetime_combined:
        timestamp_str = datetime_combined
    # Then try the hidden input (for backward compatibility)
    elif datetime_input:
        timestamp_str = datetime_input
    # Finally, construct from individual date and time components
    elif date_value and time_value:
        try:
            timestamp_str = f"{date_value} {time_value}:00"
            # Validate the timestamp by parsing it
            datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")
        except ValueError:
            return "Invalid date/time format", dash.no_update

    if not timestamp_str:
        return "Invalid date/time format", dash.no_update

    # Convert the value to string
    value_str = str(value) if value is not None else ""

    # Save the reading
    try:
        result, error = bll.record_new_reading(biomarker_id, timestamp_str, value_str)

        if result is None:
            return error, dash.no_update
        else:
            print(f"Successfully added reading ID: {result}")
            new_trigger_value = trigger_value + 1 if trigger_value is not None else 1
            return "", new_trigger_value # Increment trigger
    except Exception as e:
        print(f"Error saving reading: {str(e)}")
        return f"Error saving reading: {str(e)}", dash.no_update
