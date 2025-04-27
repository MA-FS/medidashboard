"""
dashboard.py - Callbacks for the dashboard page.
"""

import dash
try:
    import dash_bootstrap_components as dbc
except ImportError:
    # If dash_bootstrap_components is not available, create a simple replacement
    class DummyDBC:
        def __getattr__(self, name):
            return lambda *args, **kwargs: html.Div()
    dbc = DummyDBC()
from dash import Input, Output, callback, dcc, html, ALL, State, no_update
import dash_mantine_components as dmc
import pandas as pd
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from itertools import groupby
import json

from .. import bll
from ..utils import calculate_start_date
from ..components import create_biomarker_card

@callback(
    Output("add-reading-modal", "opened", allow_duplicate=True),
    Output("modal-biomarker-dropdown", "value", allow_duplicate=True),
    Output("modal-datetime-input", "value", allow_duplicate=True),
    Output("modal-date-picker", "date", allow_duplicate=True),
    Output("modal-time-picker", "value", allow_duplicate=True),
    Output("modal-value-input", "value", allow_duplicate=True),
    Output("modal-unit-display", "children", allow_duplicate=True),
    Output("modal-error-message", "children", allow_duplicate=True),
    Input({'type': 'add-reading-button', 'index': ALL}, 'n_clicks'),
    prevent_initial_call=True
)
def open_add_reading_modal_from_card(n_clicks_list):
    """Opens the Add Reading modal with the biomarker pre-selected when the card button is clicked."""
    # Check if any button was clicked
    if not any(n_clicks for n_clicks in n_clicks_list if n_clicks):
        return dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update

    # Find which button was clicked
    ctx = dash.callback_context
    if not ctx.triggered:
        return dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update

    print("Add reading button clicked from card")

    # Get the ID of the clicked button
    button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    try:
        biomarker_id = json.loads(button_id)['index']
    except:
        return dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update

    # Get the biomarker details
    biomarker = bll.get_biomarker_details(biomarker_id)
    if not biomarker:
        return dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update

    # Set up the modal with the biomarker pre-selected
    now = datetime.now()
    current_date = now.strftime("%Y-%m-%d")
    current_time = now.strftime("%H:%M")
    datetime_str = now.strftime("%Y-%m-%d %H:%M:%S")

    return True, biomarker_id, datetime_str, current_date, current_time, None, biomarker.get('unit', 'Units'), ""

@callback(
    Output("biomarker-widget-area", "children"),
    Output("category-filter-buttons", "children"),
    Output("selected-category-store", "data"),
    Input("selected-category-store", "data"),
    Input("reading-update-trigger", "data"),
    Input("dashboard-visible-biomarkers-store", "data"),
    Input("chart-time-range-store", "data"), # Add time range store as Input
    Input({"type": "category-button", "index": ALL}, "n_clicks"),
    prevent_initial_call=False
)
def update_dashboard(selected_category, reading_trigger, visible_biomarker_ids, time_range_pref, button_clicks):
    """Updates the dashboard widgets based on filters, visibility, time range, and updates."""
    ctx = dash.callback_context

    # Check if a category button was clicked
    if ctx.triggered_id and isinstance(ctx.triggered_id, dict) and ctx.triggered_id.get('type') == 'category-button':
        selected_category = ctx.triggered_id.get('index')

    print(f"Updating dashboard. Category: {selected_category}, Trigger: {reading_trigger}, Visible IDs: {visible_biomarker_ids}, Time: {time_range_pref}")

    # Add a small delay to ensure the loading animation is visible
    import time
    time.sleep(0.5)

    # Validate time_range_pref and ensure it has a default if None is loaded from store initially
    valid_time_ranges = ['30d', '90d', '6m', '1y', 'all']
    if not time_range_pref or time_range_pref not in valid_time_ranges:
        print(f"Warning: Invalid time range preference '{time_range_pref}', defaulting to '6m'")
        time_range_pref = '6m'

    all_biomarkers = bll.get_all_biomarkers_grouped()

    # Get all categories for buttons
    categories = sorted(list(set(b['category'] for b in all_biomarkers if b['category'])))

    # Ensure selected_category is valid, default to 'Lipid Profile' if not
    if selected_category is None or selected_category not in ['All'] + categories:
        selected_category = 'Lipid Profile'
        print(f"Setting default category to 'Lipid Profile'")

    # Filter biomarkers based on Category AND Visibility
    if selected_category == 'All':
        filtered_biomarkers = all_biomarkers
    else:
        filtered_biomarkers = [b for b in all_biomarkers if b['category'] == selected_category]

    if visible_biomarker_ids is None or visible_biomarker_ids == "ALL":
        # Show all biomarkers when None or "ALL" is specified
        category_filtered_biomarkers = filtered_biomarkers
        print("No visibility preference found or ALL specified, showing all category-filtered biomarkers.")
    else:
        # Apply visibility filter for specific biomarkers
        visible_set = set(visible_biomarker_ids)
        category_filtered_biomarkers = [b for b in filtered_biomarkers if b['id'] in visible_set]
        print(f"Applying visibility filter. Showing {len(category_filtered_biomarkers)} biomarkers.")

    # Create category buttons
    category_buttons = []
    for cat in ['All'] + categories:
        is_selected = cat == selected_category
        button = dbc.Button(
            cat,
            id={"type": "category-button", "index": cat},
            color="primary" if is_selected else "light",
            outline=not is_selected,
            className=f"category-button {'selected' if is_selected else ''}",
        )
        category_buttons.append(button)

    if not category_filtered_biomarkers:
        alert_message = "No biomarkers found."
        if selected_category != 'All' or (visible_biomarker_ids is not None and visible_biomarker_ids != "ALL"):
            alert_message += " Adjust category or visibility settings."
        return dbc.Alert(alert_message, color="warning"), category_buttons, selected_category

    # Calculate start date based on preference
    start_date_iso = calculate_start_date(time_range_pref)
    print(f"Calculated start date for query: {start_date_iso}")

    # Group biomarkers by category for better organization
    biomarkers_by_category = {}
    for biomarker in category_filtered_biomarkers:
        category = biomarker.get('category', 'Uncategorized')
        if category not in biomarkers_by_category:
            biomarkers_by_category[category] = []
        biomarkers_by_category[category].append(biomarker)

    # Sort categories for consistent display
    sorted_categories = sorted(biomarkers_by_category.keys())

    # Create sections for each category
    sections = []
    biomarkers_with_readings = 0
    biomarkers_without_readings = 0
    categories_with_readings = set()  # Track categories that have biomarkers with readings

    # First pass: identify which biomarkers have readings and which categories they belong to
    for category in sorted_categories:
        biomarkers = biomarkers_by_category[category]
        print(f"Processing category: {category} with {len(biomarkers)} biomarkers")

        category_has_readings = False

        for biomarker in biomarkers:
            # Fetch readings using the calculated start date
            readings = bll.get_readings_for_display(biomarker['id'], start_date=start_date_iso)

            # Debug: Log biomarker readings
            if readings and len(readings) > 0:
                biomarkers_with_readings += 1
                category_has_readings = True
                print(f"Biomarker {biomarker['name']} has {len(readings)} readings")
            else:
                biomarkers_without_readings += 1
                print(f"Biomarker {biomarker['name']} has NO readings")

        # If this category has at least one biomarker with readings, add it to the set
        if category_has_readings:
            categories_with_readings.add(category)

    # Second pass: create sections only for categories that have biomarkers with readings
    for category in sorted_categories:
        # Skip categories that don't have any biomarkers with readings
        if category not in categories_with_readings:
            continue

        biomarkers = biomarkers_by_category[category]

        # Create cards for each biomarker in this category
        cards = []
        for biomarker in biomarkers:
            # Fetch readings using the calculated start date
            readings = bll.get_readings_for_display(biomarker['id'], start_date=start_date_iso)

            # Only include biomarkers with readings
            if readings and len(readings) > 0:
                # Get reference range for this biomarker
                reference_range = bll.get_reference_range_for_biomarker(biomarker['id'])

                # Create biomarker card with readings
                card = create_biomarker_card(biomarker, readings, reference_range)
                cards.append(card)

        # Create a section for this category (we know it has at least one biomarker with readings)
        if cards:  # This check is redundant but kept for safety
            category_section = html.Div([
                html.H4(category, className="category-title"),
                dmc.SimpleGrid(
                    children=cards,
                    cols={"base": 1, "sm": 2, "lg": 3},
                    spacing="md",
                    className="mb-4"
                )
            ], className="category-section")

            sections.append(category_section)

    # Log summary of biomarkers with and without readings
    print(f"Summary: {biomarkers_with_readings} biomarkers with readings, {biomarkers_without_readings} without readings")

    # Log the number of sections created
    print(f"Created {len(sections)} sections")
    for i, section in enumerate(sections):
        print(f"Section {i+1}: {section.children[0].children}")

    # If we have biomarkers but none with readings, show a nicely styled empty state
    if biomarkers_with_readings == 0 and biomarkers_without_readings > 0:
        print("No biomarkers with readings found, returning empty state message")
        return html.Div([
            html.Div([
                html.I(className="fas fa-chart-line empty-biomarkers-icon"),
                html.H5("No biomarker readings found", className="empty-biomarkers-title"),
                html.P([
                    "Your biomarkers are set up, but there's no data to display in the selected time range. ",
                    "Try adjusting the time range or add some readings."
                ], className="empty-biomarkers-message"),
                dbc.Button([
                    html.I(className="fas fa-plus me-2"),
                    "Add Reading"
                ], id="add-reading-button", color="primary")
            ], className="empty-biomarkers-state")
        ]), category_buttons, selected_category

    # If no sections were created (which can happen if all biomarkers with readings were filtered out)
    if not sections:
        print("No sections created, returning empty state message")
        return html.Div([
            html.Div([
                html.I(className="fas fa-filter empty-biomarkers-icon"),
                html.H5("No matching biomarkers found", className="empty-biomarkers-title"),
                html.P([
                    "No biomarkers with readings found in the selected categories. ",
                    "Try selecting a different category or add some readings."
                ], className="empty-biomarkers-message"),
                dbc.Button([
                    html.I(className="fas fa-sync me-2"),
                    "Show Lipid Profile"
                ], id={"type": "category-button", "index": "Lipid Profile"}, n_clicks=0, color="primary", className="me-2"),
                dbc.Button([
                    html.I(className="fas fa-plus me-2"),
                    "Add Reading"
                ], id="add-reading-button", color="success")
            ], className="empty-biomarkers-state")
        ]), category_buttons, selected_category

    print(f"Returning {len(sections)} sections")
    return sections, category_buttons, selected_category
