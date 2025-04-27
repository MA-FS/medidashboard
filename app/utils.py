"""
utils.py - Helper functions for the MediDashboard application.

This module contains utility functions used throughout the application, including:
- Date calculation for time range filtering
- UI component generation
- Data formatting and transformation
"""

import pandas as pd
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from dash import html
import dash_bootstrap_components as dbc
import dash_mantine_components as dmc

def calculate_start_date(range_option: str):
    """
    Calculates the start date based on the selected time range option.

    This function converts a time range option (e.g., '30d', '6m') into
    an actual date by subtracting the appropriate time period from today.

    Args:
        range_option (str): The time range option. Valid options are:
            - '30d': 30 days
            - '90d': 90 days
            - '6m': 6 months
            - '1y': 1 year
            - 'all': All time (returns None)

    Returns:
        str or None: The calculated start date in ISO format (YYYY-MM-DD HH:MM:SS),
                    or None if 'all' is specified
    """
    today = datetime.now()
    if range_option == '30d':
        return (today - timedelta(days=30)).strftime("%Y-%m-%d %H:%M:%S")
    elif range_option == '90d':
        return (today - timedelta(days=90)).strftime("%Y-%m-%d %H:%M:%S")
    elif range_option == '6m':
        return (today - relativedelta(months=6)).strftime("%Y-%m-%d %H:%M:%S")
    elif range_option == '1y':
        return (today - relativedelta(years=1)).strftime("%Y-%m-%d %H:%M:%S")
    elif range_option == 'all':
        return None # No start date for all time
    else: # Default to 6 months if invalid option somehow passed
        print(f"Warning: Invalid time range option '{range_option}', defaulting to 6m.")
        return (today - relativedelta(months=6)).strftime("%Y-%m-%d %H:%M:%S")

def create_biomarker_table(biomarkers_data):
    """
    Creates a Dash Bootstrap Table from biomarker data.

    This function takes a list of biomarker dictionaries and converts it
    into a Dash Bootstrap Table with edit and delete buttons for each row.

    Args:
        biomarkers_data (list): A list of biomarker dictionaries, each containing
                               'id', 'name', 'unit', and 'category' keys

    Returns:
        dash_bootstrap_components.Table or dash_bootstrap_components.Alert:
            A Bootstrap Table component if data is provided, or an Alert if no data
    """
    if not biomarkers_data:
        return dbc.Alert("No biomarkers defined yet.", color="info")

    # Convert list of dicts to DataFrame for easier handling
    df = pd.DataFrame(biomarkers_data)

    # Select and order columns for display
    df_display = df[['name', 'unit', 'category', 'id']] # Include id for button actions

    table_header = [
        html.Thead(html.Tr([
            html.Th("Name", style={"fontWeight": "bold"}),
            html.Th("Unit", style={"fontWeight": "bold"}),
            html.Th("Category", style={"fontWeight": "bold"}),
            html.Th("Actions", style={"fontWeight": "bold", "textAlign": "center"})
        ]))
    ]

    table_body = [html.Tbody([
        html.Tr([
            html.Td(row['name']),
            html.Td(row['unit']),
            # Improved handling of None/empty category values
            html.Td(row['category'] if pd.notna(row['category']) and row['category'] else '-'),
            # Add action buttons (Edit/Delete) here in the next step
            html.Td(
                dmc.Group([
                    dmc.Button(
                        "Edit",
                        id={'type': 'edit-biomarker', 'index': row['id']},
                        size="sm",
                        color="yellow",
                        variant="filled",
                        radius="md",
                        n_clicks=0  # Initialize click count to prevent auto-triggering
                    ),
                    dmc.Button(
                        "Delete",
                        id={'type': 'delete-biomarker', 'index': row['id']},
                        size="sm",
                        color="red",
                        variant="filled",
                        radius="md",
                        n_clicks=0  # Initialize click count to prevent auto-triggering
                    ),
                ], gap="md", justify="center")
            )
        ]) for _, row in df_display.iterrows()  # Use _ instead of unused index variable
    ])]

    return dmc.Paper(
        dmc.Table(
            table_header + table_body,
            striped=True,
            highlightOnHover=True,
            withTableBorder=True,
            withColumnBorders=True
        ),
        shadow="sm",
        p="md",
        radius="md"
    )
