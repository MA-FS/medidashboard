"""
biomarkers.py - Callbacks for biomarker management.
"""

import dash
from dash import Input, Output, State, callback, ALL, ctx

from .. import bll
from ..utils import create_biomarker_table

@callback(
    Output("biomarker-modal", "opened"),
    Output("biomarker-modal-title", "children"),
    Output("biomarker-edit-id-store", "data"), # Store the id for editing
    Output("biomarker-modal-name", "value"),
    Output("biomarker-modal-unit", "value"),
    Output("biomarker-modal-category", "value"),
    Output("biomarker-modal-error-message", "children"), # Clear errors on open
    Input("add-biomarker-button", "n_clicks"),
    Input({'type': 'edit-biomarker', 'index': ALL}, 'n_clicks'),
    Input("biomarker-modal-save-button", "n_clicks"), # Close on save
    Input("biomarker-modal-cancel-button", "n_clicks"), # Close on cancel
    State("biomarker-modal", "opened"),
    prevent_initial_call=True
)
def toggle_biomarker_modal(add_clicks, edit_clicks, save_clicks, cancel_clicks, is_open):
    """Opens/closes the biomarker modal and populates it with data for editing."""
    # Check if any trigger exists
    if not ctx.triggered:
        return is_open, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update

    # Get the ID of the element that triggered the callback
    triggered_id = ctx.triggered_id

    # Check if the trigger was an edit button with a valid click
    if isinstance(triggered_id, dict) and triggered_id['type'] == 'edit-biomarker':
        # Get the index of the biomarker to edit
        biomarker_id_to_edit = triggered_id['index']

        # Find which button was clicked in the edit_clicks list
        for i, clicks in enumerate(edit_clicks):
            if clicks and clicks > 0:
                # Get the biomarker data
                biomarker_data = bll.get_biomarker_details(biomarker_id_to_edit)
                if biomarker_data:
                    return (
                        True,
                        f"Edit Biomarker: {biomarker_data['name']}",
                        biomarker_id_to_edit, # Store ID
                        biomarker_data['name'],
                        biomarker_data['unit'],
                        biomarker_data['category'],
                        "" # Clear errors
                    )
                else:
                    # Should not happen if button exists, but handle gracefully
                    return False, "Error", None, "", "", "", "Error: Biomarker not found."

    # Opening logic for Add button - only if it was actually clicked
    if triggered_id == "add-biomarker-button" and add_clicks and add_clicks > 0:
        return True, "Add New Biomarker", None, "", "", "", "" # Open add mode

    # Closing logic
    if triggered_id in ["biomarker-modal-save-button", "biomarker-modal-cancel-button"]:
        return False, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, ""

    # Default: No change in modal state unless triggered by specific buttons
    return is_open, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update

@callback(
    Output("biomarker-modal-error-message", "children", allow_duplicate=True),
    Output("biomarker-update-trigger", "data"),
    Input("biomarker-modal-save-button", "n_clicks"),
    State("biomarker-edit-id-store", "data"),
    State("biomarker-modal-name", "value"),
    State("biomarker-modal-unit", "value"),
    State("biomarker-modal-category", "value"),
    State("biomarker-update-trigger", "data"), # Get current trigger value
    prevent_initial_call=True
)
def save_biomarker(n_clicks, edit_id, name, unit, category, trigger_value):
    """Handles saving (add or update) a biomarker with enhanced validation."""
    if not n_clicks:
        return "", dash.no_update # No trigger if button not clicked

    error_message = ""
    success = False

    if edit_id is None:
        # Add new biomarker
        result, error = bll.add_new_biomarker(name, unit, category)
        if result is None: # BLL returns None, error on failure
            error_message = error
        else:
            success = True
            print(f"Added biomarker ID: {result}") # Log success
    else:
        # Update existing biomarker
        result, error = bll.update_existing_biomarker(edit_id, name, unit, category)
        if not result: # BLL returns False, error on failure
            error_message = error
        else:
            success = True
            print(f"Updated biomarker ID: {edit_id}") # Log success

    if success:
        # Increment trigger value to signal successful update
        new_trigger_value = trigger_value + 1
        return "", new_trigger_value
    else:
        # Return error message and don't update trigger
        return error_message, dash.no_update

@callback(
    Output('confirm-biomarker-delete', 'displayed'),
    Output('biomarker-delete-id-store', 'data'),
    Input({'type': 'delete-biomarker', 'index': ALL}, 'n_clicks'),
    prevent_initial_call=True,
)
def display_delete_confirmation(delete_clicks):
    """Displays the delete confirmation dialog when a delete button is clicked."""
    if not ctx.triggered_id or not any(delete_clicks):
        return False, dash.no_update

    # Get the ID from the button that was clicked
    biomarker_id_to_delete = ctx.triggered_id['index']
    print(f"Delete requested for biomarker ID: {biomarker_id_to_delete}")
    return True, biomarker_id_to_delete

@callback(
    Output("biomarker-update-trigger", "data", allow_duplicate=True),
    Output("biomarker-delete-id-store", "data", allow_duplicate=True), # Clear store after use
    # Consider adding an Alert output here for success/failure message
    Input('confirm-biomarker-delete', 'submit_n_clicks'),
    State('biomarker-delete-id-store', 'data'),
    State("biomarker-update-trigger", "data"),
    prevent_initial_call=True,
)
def handle_delete_confirmation(submit_n_clicks, biomarker_id_to_delete, trigger_value):
    """Handles the actual deletion after confirmation."""
    if not submit_n_clicks or biomarker_id_to_delete is None:
        # Dialog not confirmed or no ID stored
        return dash.no_update, None # Clear stored ID just in case

    print(f"Confirming delete for biomarker ID: {biomarker_id_to_delete}")
    success = bll.remove_biomarker(biomarker_id_to_delete)

    if success:
        print(f"Successfully deleted biomarker ID: {biomarker_id_to_delete}")
        # Increment trigger to refresh table, clear stored ID
        return trigger_value + 1, None
    else:
        print(f"Failed to delete biomarker ID: {biomarker_id_to_delete}")
        # Handle error display (e.g., show an Alert) - For now, just log
        # Don't trigger refresh, clear stored ID
        return dash.no_update, None
