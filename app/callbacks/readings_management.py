"""
readings_management.py - Callbacks for managing biomarker readings.
"""

from dash import callback, Input, Output, State, ctx, no_update, ALL
import json
import dash_bootstrap_components as dbc
from dash.exceptions import PreventUpdate

from app.components import create_readings_table
import app.bll as bll

# --- View Readings Modal Callbacks ---

@callback(
    Output("view-readings-modal", "opened"),
    Output("view-readings-modal-title", "children"),
    Output("view-readings-biomarker-id-store", "data"),
    Output("view-readings-table-container", "children"),
    Input({"type": "view-readings-button", "index": ALL}, "n_clicks"),
    Input("view-readings-close-button", "n_clicks"),
    State("view-readings-modal", "opened"),
    State("view-readings-biomarker-id-store", "data"),
    prevent_initial_call=True
)
def toggle_view_readings_modal(view_clicks, close_clicks, is_open, current_biomarker_id):
    """Opens/closes the View Readings modal and loads readings data."""
    try:
        # Check if any trigger exists
        if not ctx.triggered:
            raise PreventUpdate

        # Get the trigger information
        trigger = ctx.triggered[0]
        triggered_id = ctx.triggered_id

        # Only proceed if the button was actually clicked (n_clicks > 0)
        if trigger['value'] is None or trigger['value'] <= 0:
            return is_open, no_update, no_update, no_update

        # Handle the "View Readings" button click
        if isinstance(triggered_id, dict) and triggered_id.get('type') == 'view-readings-button':
            try:
                biomarker_id = triggered_id.get('index')
                print(f"View readings clicked for biomarker ID: {biomarker_id}")

                # Get biomarker details
                biomarker = bll.get_biomarker_details(biomarker_id)
                if not biomarker:
                    # Handle error
                    print(f"Error: Biomarker with ID {biomarker_id} not found")
                    return is_open, "Error: Biomarker not found", no_update, no_update

                # Get all readings for this biomarker (no date filtering)
                readings = bll.get_readings_for_display(biomarker_id)
                print(f"Retrieved {len(readings)} readings for biomarker {biomarker['name']}")

                # Create the table
                table = create_readings_table(readings, biomarker['unit'])

                # Set the modal title
                title = f"Readings for {biomarker['name']} ({biomarker['unit']})"

                return True, title, biomarker_id, table
            except Exception as e:
                print(f"Error processing view readings button click: {str(e)}")
                import traceback
                traceback.print_exc()
                return is_open, f"Error: {str(e)}", no_update, no_update

        # Handle the "Close" button click
        elif triggered_id == "view-readings-close-button":
            return False, no_update, no_update, no_update

        # Default: No change in modal state
        return is_open, no_update, no_update, no_update
    except Exception as e:
        print(f"Error in toggle_view_readings_modal: {str(e)}")
        import traceback
        traceback.print_exc()
        return is_open, f"Error: {str(e)}", no_update, no_update

# --- Delete Reading Confirmation Modal Callbacks ---

@callback(
    Output("delete-reading-confirm-modal", "opened"),
    Output("delete-reading-id-store", "data"),
    Input({"type": "delete-reading-button", "index": ALL}, "n_clicks"),
    Input("delete-reading-confirm-button", "n_clicks"),
    Input("delete-reading-cancel-button", "n_clicks"),
    State("delete-reading-confirm-modal", "opened"),
    prevent_initial_call=True
)
def toggle_delete_reading_confirm_modal(delete_clicks, confirm_clicks, cancel_clicks, is_open):
    """Opens/closes the Delete Reading confirmation modal."""
    # Check if any trigger exists
    if not ctx.triggered:
        raise PreventUpdate

    # Get the trigger information
    trigger = ctx.triggered[0]
    triggered_id = ctx.triggered_id

    # Only proceed if the button was actually clicked (n_clicks > 0)
    if trigger['value'] is None or trigger['value'] <= 0:
        return is_open, no_update

    # Handle the "Delete" button click in the readings table
    if isinstance(triggered_id, dict) and triggered_id.get('type') == 'delete-reading-button':
        reading_id = triggered_id.get('index')
        return True, reading_id

    # Handle the "Confirm" or "Cancel" button click
    elif triggered_id in ["delete-reading-confirm-button", "delete-reading-cancel-button"]:
        return False, no_update

    # Default: No change in modal state
    return is_open, no_update

# --- Delete Reading Callback ---

@callback(
    Output("view-readings-error-message", "children"),
    Output("view-readings-table-container", "children", allow_duplicate=True),
    Output("reading-update-trigger", "data", allow_duplicate=True),
    Input("delete-reading-confirm-button", "n_clicks"),
    State("delete-reading-id-store", "data"),
    State("view-readings-biomarker-id-store", "data"),
    State("reading-update-trigger", "data"),
    prevent_initial_call=True
)
def delete_reading(confirm_clicks, reading_id, biomarker_id, trigger_value):
    """Deletes a reading when confirmed."""
    # Check if the confirm button was actually clicked
    if not confirm_clicks or confirm_clicks <= 0:
        raise PreventUpdate

    # Check if we have a valid reading ID
    if not reading_id:
        return "Error: No reading selected for deletion", no_update, no_update

    # Delete the reading
    success, error_message = bll.delete_biomarker_reading(reading_id)

    if not success:
        return error_message, no_update, no_update

    # If successful, refresh the readings table
    biomarker = bll.get_biomarker_details(biomarker_id)
    readings = bll.get_readings_for_display(biomarker_id)
    table = create_readings_table(readings, biomarker['unit'])

    # Increment the trigger to refresh the dashboard
    new_trigger_value = trigger_value + 1 if trigger_value is not None else 1

    return "", table, new_trigger_value
