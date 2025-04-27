"""
components.py - Reusable UI components for the MediDashboard application.
"""

from dash import dcc, html
import dash_mantine_components as dmc
import dash_bootstrap_components as dbc
import pandas as pd
from datetime import datetime
import altair as alt
import base64
from io import BytesIO

# --- Helper Functions ---
def create_sparkline_chart(readings, reference_range=None):
    """
    Creates an Altair chart for biomarker readings with full axes and risk zones.
    Implements Apple-style design with smooth curves, subtle gradients, and interactive elements.

    Args:
        readings (list): List of reading dictionaries with 'timestamp' and 'value' keys
        reference_range (dict, optional): Reference range information with 'range_type',
                                         'lower_bound', and 'upper_bound' keys

    Returns:
        altair.Chart: An Altair chart object with full visualization features
    """
    # Apple-style color palette
    APPLE_COLORS = {
        'blue': '#007AFF',       # Primary blue
        'green': '#34C759',      # Success green
        'orange': '#FF9500',     # Warning orange
        'red': '#FF3B30',        # Error/danger red
        'gray': '#8E8E93',       # Neutral gray
        'light_gray': '#E5E5EA', # Light gray for backgrounds
        'dark_gray': '#3A3A3C',  # Dark gray for text
        'background': '#F2F2F7', # Background color
    }
    if not readings:
        # No readings at all
        print("No readings provided to create_sparkline_chart")
        return None

    # Even with just one reading, we'll create a chart
    print(f"Creating chart with {len(readings)} readings")

    # Debug: Print the first reading to see its structure
    if readings:
        print(f"First reading: {readings[0]}")

    # Convert readings to DataFrame for Altair
    df = pd.DataFrame(readings)

    # Ensure timestamp is in datetime format
    df['timestamp'] = pd.to_datetime(df['timestamp'])

    # Sort by timestamp (ascending)
    df = df.sort_values('timestamp')

    # Debug: Print the dataframe info
    print(f"DataFrame shape: {df.shape}")
    print(f"DataFrame columns: {df.columns}")

    # Make sure 'value' column is numeric
    try:
        df['value'] = pd.to_numeric(df['value'])
        print(f"Value column converted to numeric. Min: {df['value'].min()}, Max: {df['value'].max()}")
    except Exception as e:
        print(f"Error converting value column to numeric: {e}")
        # If conversion fails, try to fix the data
        if 'value' in df.columns:
            print(f"Value column types: {df['value'].apply(type).unique()}")
            # Try to handle each value individually
            for i, val in enumerate(df['value']):
                try:
                    df.at[i, 'value'] = float(val)
                except:
                    print(f"Could not convert value at index {i}: {val}")
                    # Set to a default value to avoid breaking the chart
                    df.at[i, 'value'] = 0.0

    # Extract min and max values from the data
    data_min = df['value'].min()
    data_max = df['value'].max()
    data_mean = df['value'].mean()  # Calculate the mean of the data

    # Calculate the data range
    data_range = data_max - data_min

    # Calculate a significance threshold (20% of the mean instead of 10%)
    # This determines what we consider a significant change in the data
    significance_threshold = data_mean * 0.20 if data_mean > 0 else 1.0

    # Determine if the data has low variation (range is less than significance threshold)
    low_variation = data_range < significance_threshold

    # For extremely low variation (less than 5% of mean), we'll zoom in even more
    very_low_variation = data_range < data_mean * 0.05 and data_mean > 0

    # Debug logging
    print(f"Data min: {data_min}, max: {data_max}, mean: {data_mean}, range: {data_range}")
    print(f"Significance threshold: {significance_threshold}, low variation: {low_variation}")

    if very_low_variation:
        # For extremely low variation, use a very tight zoom
        min_value = data_min * 0.9  # Start at 90% of minimum
        max_value = data_max * 1.1  # End at 110% of maximum
        print(f"Very low variation detected, using tight zoom: {min_value} to {max_value}")
    elif low_variation and data_mean > 0:
        # For low variation data, center the domain around the mean with a minimum range
        # This will zoom in to show small variations more clearly
        padding_factor = 1.2  # Use 1.2x instead of 1.5x for tighter zoom
        min_value = data_mean - significance_threshold * padding_factor
        max_value = data_mean + significance_threshold * padding_factor

        # Ensure min_value is not negative for values that should be positive
        if min_value < 0 and data_min >= 0:
            min_value = 0
            # Adjust max_value to maintain the same range
            max_value = significance_threshold * padding_factor * 2

        # For values significantly above zero, ensure we don't start the axis at 0
        if data_min > data_mean * 0.5 and min_value < data_min * 0.8:
            min_value = data_min * 0.8  # Start at 80% of the minimum value
    else:
        # For normal variation data, use percentage padding
        min_value = data_min * 0.85  # 15% padding below
        max_value = data_max * 1.15  # 15% padding above

        # Ensure min_value is not negative for values that should be positive
        if min_value < 0 and data_min >= 0:
            min_value = 0

    # Calculate the data span (the range of actual values)
    data_span = data_max - data_min
    # Use a minimum span to avoid division issues with identical values
    min_span = max(data_span, data_mean * 0.1) if data_mean > 0 else 1.0

    # Debug logging for scaling calculations
    print(f"Data range: {data_min} to {data_max}, span: {data_span}")
    print(f"Initial scale range: {min_value} to {max_value}")

    # For a single reading, we need to create a synthetic second point for the chart
    # This will allow us to draw a proper chart even with just one reading
    if len(df) == 1:
        # Get the single reading
        single_timestamp = df['timestamp'].iloc[0]

        # Create a synthetic second point 30 days before with the same value
        # This creates a flat line showing the current value
        synthetic_timestamp = single_timestamp - pd.Timedelta(days=30)

        # Create a copy of the first row for our synthetic point
        synthetic_row = df.iloc[0].copy()

        # Update the timestamp and ensure id is unique
        synthetic_row['timestamp'] = synthetic_timestamp
        if 'id' in synthetic_row:
            synthetic_row['id'] = -1  # Use -1 as a special ID for the synthetic point

        # Add the synthetic point to the dataframe
        synthetic_df = pd.DataFrame([synthetic_row])

        # Combine with the original dataframe
        df = pd.concat([synthetic_df, df]).reset_index(drop=True)

    # Get reference ranges for color zones
    lower_bound = None
    upper_bound = None
    range_type = None
    if reference_range:
        range_type = reference_range.get('range_type')
        lower_bound = reference_range.get('lower_bound')
        upper_bound = reference_range.get('upper_bound')

        # Adjust min and max values to include reference range, but with limits
        if lower_bound is not None:
            # Calculate how far the lower bound is from the data
            distance_to_lower = data_min - lower_bound if lower_bound < data_min else 0

            if low_variation:
                # For low variation data, include reference bounds but don't extend too much
                if lower_bound < min_value:
                    # If we're in low variation mode and the lower bound is outside our range
                    if distance_to_lower > significance_threshold * 2:
                        # If it's very far, only extend partially
                        min_value = min(min_value, data_mean - significance_threshold * 2)
                    else:
                        # If it's reasonably close, include it
                        min_value = min(min_value, lower_bound * 0.95)
            else:
                # For normal variation data, use the existing approach
                if distance_to_lower <= 2 * min_span:
                    min_value = min(min_value, lower_bound * 0.85)
                else:
                    # Otherwise, extend partially toward the lower bound
                    min_value = min(min_value, data_min - min_span)

        if upper_bound is not None:
            # Calculate how far the upper bound is from the data
            distance_to_upper = upper_bound - data_max if upper_bound > data_max else 0

            if low_variation:
                # For low variation data, include reference bounds but don't extend too much
                if upper_bound > max_value:
                    # If we're in low variation mode and the upper bound is outside our range
                    if distance_to_upper > significance_threshold * 2:
                        # If it's very far, only extend partially
                        max_value = max(max_value, data_mean + significance_threshold * 2)
                    else:
                        # If it's reasonably close, include it
                        max_value = max(max_value, upper_bound * 1.05)
            else:
                # For normal variation data, use the existing approach
                if distance_to_upper <= 2 * min_span:
                    max_value = max(max_value, upper_bound * 1.15)
                else:
                    # Otherwise, extend partially toward the upper bound
                    max_value = max(max_value, data_max + min_span)

        # Debug logging for final scale after reference range adjustments
        print(f"Reference range: {range_type}, lower: {lower_bound}, upper: {upper_bound}")
        print(f"Final scale range: {min_value} to {max_value}")

    # Create background layers for reference ranges with solid colors
    background_layers = []
    if reference_range:
        if range_type == 'between' and lower_bound is not None and upper_bound is not None:
            # Normal range (between lower and upper bounds) - subtle green
            background_layers.append(
                alt.Chart(pd.DataFrame({
                    'y1': [lower_bound],
                    'y2': [upper_bound]
                })).mark_rect(
                    color=APPLE_COLORS['green'],
                    opacity=0.18  # Slightly more opaque for better visibility
                ).encode(
                    y='y1:Q',
                    y2='y2:Q'
                )
            )

            # Below range - subtle red
            background_layers.append(
                alt.Chart(pd.DataFrame({
                    'y1': [min_value],
                    'y2': [lower_bound]
                })).mark_rect(
                    color=APPLE_COLORS['red'],
                    opacity=0.18  # Slightly more opaque for better visibility
                ).encode(
                    y='y1:Q',
                    y2='y2:Q'
                )
            )

            # Above range - subtle red
            background_layers.append(
                alt.Chart(pd.DataFrame({
                    'y1': [upper_bound],
                    'y2': [max_value]
                })).mark_rect(
                    color=APPLE_COLORS['red'],
                    opacity=0.18  # Slightly more opaque for better visibility
                ).encode(
                    y='y1:Q',
                    y2='y2:Q'
                )
            )
        elif range_type == 'below' and upper_bound is not None:
            # Normal range (below upper_bound) - subtle green
            background_layers.append(
                alt.Chart(pd.DataFrame({
                    'y1': [min_value],
                    'y2': [upper_bound]
                })).mark_rect(
                    color=APPLE_COLORS['green'],
                    opacity=0.18  # Slightly more opaque for better visibility
                ).encode(
                    y='y1:Q',
                    y2='y2:Q'
                )
            )

            # Above range - subtle red
            background_layers.append(
                alt.Chart(pd.DataFrame({
                    'y1': [upper_bound],
                    'y2': [max_value]
                })).mark_rect(
                    color=APPLE_COLORS['red'],
                    opacity=0.18  # Slightly more opaque for better visibility
                ).encode(
                    y='y1:Q',
                    y2='y2:Q'
                )
            )
        elif range_type == 'above' and lower_bound is not None:
            # Below range - subtle red
            background_layers.append(
                alt.Chart(pd.DataFrame({
                    'y1': [min_value],
                    'y2': [lower_bound]
                })).mark_rect(
                    color=APPLE_COLORS['red'],
                    opacity=0.18  # Slightly more opaque for better visibility
                ).encode(
                    y='y1:Q',
                    y2='y2:Q'
                )
            )

            # Normal range (above lower_bound) - subtle green
            background_layers.append(
                alt.Chart(pd.DataFrame({
                    'y1': [lower_bound],
                    'y2': [max_value]
                })).mark_rect(
                    color=APPLE_COLORS['green'],
                    opacity=0.18  # Slightly more opaque for better visibility
                ).encode(
                    y='y1:Q',
                    y2='y2:Q'
                )
            )

    # Add formatted date and value to the dataframe for tooltips
    df['formatted_date'] = df['timestamp'].dt.strftime('%b %d, %Y')
    df['formatted_value'] = df['value'].apply(lambda x: f"{x:.2f}")

    # Create the base chart with proper axes and tooltips
    base = alt.Chart(df).encode(
        x=alt.X('timestamp:T',
                axis=alt.Axis(
                    format='%b',  # Format as "Apr" (month only to save space)
                    labelAngle=0,  # Horizontal labels for better readability
                    title=None,
                    labelColor=APPLE_COLORS['gray'],
                    labelFont='SF Pro Display, -apple-system, BlinkMacSystemFont, sans-serif',
                    labelFontSize=9,  # Slightly larger font for better readability
                    tickColor=APPLE_COLORS['light_gray'],
                    domainColor=APPLE_COLORS['light_gray'],
                    labelOverlap='parity',  # Handle label overlap
                    labelLimit=30,  # Limit label width
                    labelPadding=2,  # Minimal padding for better space usage
                    tickCount=4  # Limit the number of ticks to prevent overcrowding
                )),
        y=alt.Y('value:Q',
                scale=alt.Scale(
                    domain=[min_value, max_value],
                    nice=True,  # Use nice round numbers for axis ticks
                    zero=False  # Explicitly prevent starting at zero
                ),
                axis=alt.Axis(
                    title=None,
                    labelColor=APPLE_COLORS['gray'],
                    labelFont='SF Pro Display, -apple-system, BlinkMacSystemFont, sans-serif',
                    labelFontSize=9,  # Slightly larger font for better readability
                    tickColor=APPLE_COLORS['light_gray'],
                    domainColor=APPLE_COLORS['light_gray'],
                    grid=True,
                    gridColor=APPLE_COLORS['light_gray'],
                    gridOpacity=0.3,
                    gridDash=[2, 2],
                    labelLimit=30,  # Limit label width
                    labelPadding=2,  # Minimal padding for better space usage
                    tickCount=4  # Fewer ticks for cleaner appearance
                )),
        tooltip=[
            alt.Tooltip('formatted_date:N', title='Date'),
            alt.Tooltip('formatted_value:N', title='Value')
        ]
    )

    # Create the line chart with smooth interpolation
    line = base.mark_line(
        color=APPLE_COLORS['blue'],
        strokeWidth=2.5,  # Slightly thicker line for better visibility
        interpolate='monotone',  # Smooth, curved lines
        strokeOpacity=0.9  # Slightly more opaque for better visibility
    )

    # Create a single hover selection
    hover = alt.selection_single(
        on='mouseover',
        nearest=True,
        fields=['timestamp'],
        empty='none',
        name='hover'  # Give it a specific name to avoid conflicts
    )

    # Add points at each data point with interactive hover effects
    points = base.mark_point(
        color=APPLE_COLORS['blue'],
        filled=True,
        shape='circle'
    ).encode(
        size=alt.condition(hover, alt.value(100), alt.value(60)),  # Slightly smaller points
        opacity=alt.condition(hover, alt.value(1), alt.value(0.8)),
        stroke=alt.condition(hover, alt.value('white'), alt.value(None)),
        strokeWidth=alt.condition(hover, alt.value(2), alt.value(0))
    ).add_selection(hover)

    # Add text labels with values only on hover for cleaner look
    text = base.mark_text(
        align='center',
        baseline='bottom',
        dy=-10,  # Offset above the point
        fontSize=11,  # Slightly smaller font size
        fontWeight='bold',
        font='SF Pro Display, -apple-system, BlinkMacSystemFont, sans-serif',
        color=APPLE_COLORS['dark_gray']
    ).encode(
        text=alt.Text('value:Q', format='.1f'),  # Format with 1 decimal place
        opacity=alt.condition(hover, alt.value(1), alt.value(0))
    )

    # Add reference lines if provided - using dotted lines for better visibility
    reference_layers = []
    if reference_range:
        if lower_bound is not None:
            reference_layers.append(
                alt.Chart(pd.DataFrame({'y': [lower_bound]})).mark_rule(
                    color=APPLE_COLORS['orange'],
                    strokeDash=[4, 2],
                    strokeWidth=1.5,  # Slightly thicker for better visibility
                    opacity=0.8  # Slightly more opaque for better visibility
                ).encode(
                    y='y:Q',
                    tooltip=alt.Tooltip('y:Q', title='Lower Bound', format='.2f')
                )
            )
        if upper_bound is not None:
            reference_layers.append(
                alt.Chart(pd.DataFrame({'y': [upper_bound]})).mark_rule(
                    color=APPLE_COLORS['red'],
                    strokeDash=[4, 2],
                    strokeWidth=1.5,  # Slightly thicker for better visibility
                    opacity=0.8  # Slightly more opaque for better visibility
                ).encode(
                    y='y:Q',
                    tooltip=alt.Tooltip('y:Q', title='Upper Bound', format='.2f')
                )
            )

    # Combine all layers
    chart = alt.layer(*background_layers) if background_layers else alt.Chart()
    for layer in reference_layers:
        chart += layer
    chart += line + points + text

    # Configure the chart appearance with a simpler configuration
    chart = chart.configure_view(
        strokeWidth=0,
        strokeOpacity=0,
        continuousHeight=180,  # Increase height to provide more space
        continuousWidth=320    # Maintain width to fit container
    ).properties(
        width='container',  # Responsive width to fit container
        height=180,         # Increased height to accommodate labels
        padding={'left': 5, 'right': 5, 'top': 5, 'bottom': 20},  # Minimal padding to maximize chart area
        autosize={'type': 'fit', 'contains': 'padding'},  # Ensure chart fits within container
        usermeta={"embedOptions": {"actions": False}}  # Disable the three-dot menu
    ).configure_axis(
        grid=False,
        labelColor=APPLE_COLORS['gray'],
        domainColor=APPLE_COLORS['light_gray'],
        labelFontSize=9,  # Slightly larger font for better readability
        labelLimit=80,    # Limit label width to prevent overflow
        labelPadding=2,   # Minimal padding for labels
        tickSize=3        # Smaller tick marks
    )

    return chart

def embed_altair_chart(chart, height=180):
    """
    Embeds an Altair chart in a Dash application with responsive design.

    Args:
        chart (altair.Chart): The Altair chart to embed
        height (int, optional): Height of the iframe in pixels

    Returns:
        dash_html_components.Iframe: An iframe component with the embedded chart
    """
    if chart is None:
        return html.Div("No data for chart", className="text-muted small")

    # Convert chart to HTML with minimal options and specific sizing
    html_str = chart.to_html(
        embed_options={
            'actions': False,
            'renderer': 'svg',  # Use SVG renderer for better control
            'scaleFactor': 1.0  # Ensure proper scaling
        }
    )

    # Create a unique ID for the iframe
    import uuid
    iframe_id = f"chart-{uuid.uuid4()}"

    # Create an iframe to embed the chart
    iframe = html.Iframe(
        id=iframe_id,
        srcDoc=html_str,
        style={
            'border': 'none',
            'width': '100%',  # Use 100% width to fill container
            'height': f"{height}px",
            'overflow': 'hidden',  # Force hidden overflow
            'display': 'block',
            'margin': '0',
            'padding': '0',
            'borderRadius': '8px',  # Rounded corners for Apple-style
            'boxShadow': '0 1px 3px rgba(0,0,0,0.1)'  # Subtle shadow for depth
        },
        sandbox="allow-scripts",  # Allow scripts but restrict other features
        className="biomarker-chart"
    )

    return iframe

def create_readings_table(readings, biomarker_unit):
    """
    Creates a table displaying biomarker readings with delete buttons.

    Args:
        readings (list): List of reading dictionaries
        biomarker_unit (str): The unit of the biomarker

    Returns:
        dash_bootstrap_components.Table: A Bootstrap Table component
    """
    if not readings:
        return dbc.Alert("No readings found for this biomarker.", color="info")

    # Convert to DataFrame for easier manipulation
    df = pd.DataFrame(readings)

    # Sort by timestamp in descending order (newest first)
    df = df.sort_values('timestamp', ascending=False)

    # Create the table header
    header = html.Thead([
        html.Tr([
            html.Th("Date & Time"),
            html.Th(f"Value ({biomarker_unit})"),
            html.Th("Actions")
        ])
    ])

    # Create the table body
    rows = []
    for _, row in df.iterrows():
        # Format the timestamp
        timestamp = row['timestamp']
        if isinstance(timestamp, str):
            # If it's a string, try to parse it
            try:
                dt = datetime.fromisoformat(timestamp)
                formatted_time = dt.strftime("%Y-%m-%d %H:%M")
            except ValueError:
                formatted_time = timestamp
        else:
            # If it's already a datetime object
            formatted_time = timestamp.strftime("%Y-%m-%d %H:%M")

        # Format the value
        value = row['value']
        if isinstance(value, float):
            # For very small numbers (scientific notation)
            if abs(value) < 0.01:
                # Format as scientific notation but with better presentation
                base, exponent = f"{value:.2e}".split('e')
                # Remove leading + and convert to proper format
                exponent = exponent.replace('+', '')
                formatted_value = f"{base}×10{exponent}"
            # For large numbers (over 1000)
            elif abs(value) >= 1000:
                # Format with commas for thousands separator
                formatted_value = f"{value:,.2f}"
            # For zero values, show as plain 0.00
            elif abs(value) < 0.000001:
                formatted_value = "0.00"
            # For normal range values
            else:
                formatted_value = f"{value:.2f}"  # 2 decimal places
        else:
            formatted_value = str(value)

        # Create the row
        tr = html.Tr([
            html.Td(formatted_time),
            html.Td(formatted_value),
            html.Td(
                dmc.Group([
                    # Edit button
                    dmc.ActionIcon(
                        html.I(className="fas fa-edit"),
                        id={'type': 'edit-reading-button', 'index': row['id']},
                        color="yellow",
                        variant="filled",
                        size="md",
                        radius="md"
                    ),
                    # Delete button
                    dmc.ActionIcon(
                        html.I(className="fas fa-trash"),
                        id={'type': 'delete-reading-button', 'index': row['id']},
                        color="red",
                        variant="filled",
                        size="md",
                        radius="md"
                    )
                ], gap="md", justify="center")
            )
        ])
        rows.append(tr)

    body = html.Tbody(rows)

    # Create the table
    table = dbc.Table([header, body], bordered=True, hover=True, responsive=True, striped=True)

    return table

# --- Navbar Component ---
# Create a brand element with logo and text
brand = dmc.Group([
    dmc.Image(src="/assets/logo.png", h=30, w="auto"),
    dmc.Text("MediDashboard", fw=700, size="lg", c="white")  # Explicitly set text color to white
], gap="xs")

# Create dark mode toggle with improved styling
dark_mode_toggle = dmc.ActionIcon(
    html.I(className="fas fa-moon", id="dark-mode-icon"),
    id="dark-mode-toggle",
    variant="filled",
    color="blue",
    radius="xl",
    size="lg",
    style={
        "boxShadow": "0 2px 8px rgba(0, 0, 0, 0.15)",
        "transition": "all 0.3s ease",
        "background": "rgba(255, 255, 255, 0.2)",
        "border": "1px solid rgba(255, 255, 255, 0.3)",
        "backdropFilter": "blur(5px)",
        "WebkitBackdropFilter": "blur(5px)"
    },
    className="dark-mode-toggle"
)

# Create navbar links
navbar_links = dmc.Group([
    dmc.Anchor("Dashboard", href="/", underline=False, c="white"),
    dmc.Anchor("Settings", href="/settings", underline=False, c="white"),
    dark_mode_toggle
], justify="flex-end")

# Create the navbar
navbar = html.Div(
    style={
        "height": "60px",
        "position": "fixed",
        "top": 0,
        "left": 0,
        "right": 0,
        "padding": "var(--mantine-spacing-md)",
        "background": "linear-gradient(135deg, var(--mantine-color-blue-7) 0%, var(--mantine-color-blue-5) 100%)",
        "color": "white",
        "marginBottom": "0px",
        "zIndex": 100,
        "boxShadow": "0 2px 10px rgba(0, 0, 0, 0.1)",
        "backdropFilter": "blur(10px)",
        "WebkitBackdropFilter": "blur(10px)"
    },
    children=[
        dmc.Container(
            fluid=True,
            children=dmc.Group([
                dmc.Anchor(brand, href="/", underline=False),
                navbar_links
            ], justify="space-between", align="center")
        )
    ]
)

# --- View Readings Modal Structure ---
view_readings_modal = dmc.Modal(
    title=dmc.Group([
        html.I(className="fas fa-chart-line me-2", style={"color": "var(--mantine-color-blue-6)"}),
        dmc.Text(id="view-readings-modal-title", fw=700, size="lg")
    ]),
    styles={
        "modal": {
            "borderRadius": "16px",
            "boxShadow": "0 10px 40px rgba(0, 0, 0, 0.15)",
        },
        "header": {
            "backgroundColor": "var(--mantine-color-gray-0)",
            "borderBottom": "1px solid var(--mantine-color-gray-2)",
            "padding": "20px 24px",
        },
        "body": {
            "padding": "24px",
        }
    },
    children=[
        # Hidden store to keep track of the biomarker ID
        dcc.Store(id='view-readings-biomarker-id-store', data=None),
        # Table to display readings
        html.Div(id="view-readings-table-container"),
        # Error message area
        dmc.Text(id="view-readings-error-message", c="red", mt="md"),
        # Footer with close button
        dmc.Group(
            [
                dmc.Button(
                    "Close",
                    id="view-readings-close-button",
                    variant="outline",
                    color="gray",
                    radius="md",
                    size="md",
                    leftSection=html.I(className="fas fa-times")
                )
            ],
            justify="flex-end",
            mt="xl"
        )
    ],
    id="view-readings-modal",
    size="lg",
    opened=False,
    transitionProps={"duration": 300, "transition": "slide-up"},
    overlayProps={"blur": 5, "opacity": 0.55},
    centered=True,
    shadow="xl"
)

# --- Delete Reading Confirmation Modal ---
delete_reading_confirm_modal = dmc.Modal(
    title=dmc.Group([
        html.I(className="fas fa-trash-alt me-2", style={"color": "var(--mantine-color-red-6)"}),
        dmc.Text("Confirm Deletion", fw=700, size="lg")
    ]),
    styles={
        "modal": {
            "borderRadius": "16px",
            "boxShadow": "0 10px 40px rgba(0, 0, 0, 0.15)",
        },
        "header": {
            "backgroundColor": "var(--mantine-color-gray-0)",
            "borderBottom": "1px solid var(--mantine-color-gray-2)",
            "padding": "20px 24px",
        },
        "body": {
            "padding": "24px",
        }
    },
    children=[
        # Hidden store to keep track of the reading ID to delete
        dcc.Store(id='delete-reading-id-store', data=None),
        dmc.Alert(
            title="Warning",
            color="red",
            children="Are you sure you want to delete this reading? This action cannot be undone.",
            icon=html.I(className="fas fa-exclamation-triangle"),
            mb="md"
        ),
        # Footer with buttons
        dmc.Group(
            [
                dmc.Button(
                    "Delete",
                    id="delete-reading-confirm-button",
                    color="red",
                    variant="filled",
                    radius="md",
                    size="md",
                    leftSection=html.I(className="fas fa-trash-alt")
                ),
                dmc.Button(
                    "Cancel",
                    id="delete-reading-cancel-button",
                    variant="outline",
                    color="gray",
                    radius="md",
                    size="md"
                )
            ],
            justify="flex-end",
            mt="xl"
        )
    ],
    id="delete-reading-confirm-modal",
    opened=False,
    transitionProps={"duration": 300, "transition": "slide-up"},
    overlayProps={"blur": 5, "opacity": 0.55},
    centered=True,
    shadow="xl"
)

# --- Edit Reading Modal ---
edit_reading_modal = dmc.Modal(
    title=dmc.Group([
        html.I(className="fas fa-edit me-2", style={"color": "var(--mantine-color-blue-6)"}),
        dmc.Text("Edit Reading", fw=700, size="lg")
    ]),
    styles={
        "modal": {
            "borderRadius": "16px",
            "boxShadow": "0 10px 40px rgba(0, 0, 0, 0.15)",
        },
        "header": {
            "backgroundColor": "var(--mantine-color-gray-0)",
            "borderBottom": "1px solid var(--mantine-color-gray-2)",
            "padding": "20px 24px",
        },
        "body": {
            "padding": "24px",
        }
    },
    children=[
        # Hidden stores to keep track of the reading ID and biomarker ID
        dcc.Store(id='edit-reading-id-store', data=None),
        dcc.Store(id='edit-reading-biomarker-id-store', data=None),
        dcc.Store(id='edit-reading-biomarker-unit-store', data=None),
        dcc.Store(id="edit-reading-datetime-combined", data=None),

        # Date and time inputs
        dmc.Grid(
            [
                dmc.GridCol(dmc.Text("Date & Time:", fw=500), span=3),
                dmc.GridCol([
                    # Date picker
                    dmc.Text("Date:", fw=500, mb="xs"),
                    dmc.DatePickerInput(
                        id="edit-reading-date-picker",
                        valueFormat="YYYY-MM-DD",
                        mb="md",
                        w="100%"
                    ),
                    # Time picker
                    dmc.Text("Time:", fw=500, mb="xs"),
                    dmc.TimeInput(
                        id="edit-reading-time-picker",
                        withSeconds=False,
                        w="100%"
                    )
                ], span=9)
            ],
            mb="md"
        ),

        # Value input
        dmc.Grid(
            [
                dmc.GridCol(dmc.Text("Value:", fw=500), span=3),
                dmc.GridCol([
                    dmc.Group([
                        dmc.NumberInput(
                            id="edit-reading-value-input",
                            placeholder="Enter value",
                            w="70%"
                        ),
                        dmc.Text(id="edit-reading-unit-display", w="30%")
                    ], grow=True)
                ], span=9)
            ],
            mb="md"
        ),

        # Error message area
        dmc.Text(id="edit-reading-error-message", c="red", mt="md"),

        # Footer with buttons
        dmc.Group(
            [
                dmc.Button(
                    "Save",
                    id="edit-reading-save-button",
                    color="blue",
                    variant="filled",
                    radius="md",
                    size="md",
                    leftSection=html.I(className="fas fa-save")
                ),
                dmc.Button(
                    "Cancel",
                    id="edit-reading-cancel-button",
                    variant="outline",
                    color="gray",
                    radius="md",
                    size="md"
                )
            ],
            justify="flex-end",
            mt="xl"
        )
    ],
    id="edit-reading-modal",
    opened=False,
    size="md",
    transitionProps={"duration": 300, "transition": "slide-up"},
    overlayProps={"blur": 5, "opacity": 0.55},
    centered=True,
    shadow="xl"
)

# --- CSV Preview and Validation Components ---
def create_csv_preview_table(preview_data, row_results=None):
    """
    Creates a table to preview CSV data with validation status.

    Args:
        preview_data (list): List of dictionaries representing CSV rows
        row_results (list, optional): Validation results for each row

    Returns:
        dash component: A table component showing the CSV preview with validation status
    """
    if not preview_data:
        return html.Div("No data to preview")

    # Create header
    columns = list(preview_data[0].keys())

    # Move 'Row Number' to the beginning if it exists
    if 'Row Number' in columns:
        columns.remove('Row Number')
        display_columns = ['Row Number'] + columns
    else:
        display_columns = columns

    header = html.Thead(html.Tr([html.Th("Status")] + [html.Th(col) for col in display_columns] + [html.Th("Actions")]))

    # Create rows
    rows = []
    for i, row in enumerate(preview_data):
        # Determine row status
        status_icon = html.I(className="fas fa-check-circle text-success")
        row_class = ""
        tooltip_text = "Valid"

        # Get the actual row number from the data if available, otherwise use the index
        row_number = row.get('Row Number', i + 2)  # +2 for header and 0-indexing

        # Find the corresponding validation result
        result = None
        if row_results:
            # Try to find by row number first
            for r in row_results:
                if r['row_number'] == row_number:
                    result = r
                    break

            # If not found and we're within range, use the index
            if result is None and i < len(row_results):
                result = row_results[i]

        # Update status based on validation result
        if result and not result['is_valid']:
            status_icon = html.I(className="fas fa-exclamation-circle text-danger")
            row_class = "table-danger"
            tooltip_text = ", ".join(result['issues'])

        # Create status cell with tooltip
        status_cell = html.Td(
            [
                html.Div(
                    status_icon,
                    id=f"row-status-{i}"
                ),
                dbc.Tooltip(
                    tooltip_text,
                    target=f"row-status-{i}",
                    placement="top"
                )
            ]
        )

        # Create row cells
        cells = [status_cell]

        # Add cells in the correct order
        for col in display_columns:
            cell_value = row.get(col, "")
            cells.append(html.Td(str(cell_value)))

        # Add delete button
        delete_button = dbc.Button(
            html.I(className="fas fa-trash"),
            id={"type": "csv-delete-row", "index": i},
            color="danger",
            size="sm",
            className="me-1",
            title="Delete Row"
        )

        cells.append(html.Td(delete_button))

        # Add row to rows list
        rows.append(html.Tr(cells, className=row_class))

    # Create table body
    body = html.Tbody(rows)

    # Create table with scrollable container for large datasets
    table_container = html.Div(
        dbc.Table(
            [header, body],
            bordered=True,
            hover=True,
            responsive=True,
            striped=True,
            className="csv-preview-table"
        ),
        style={
            "maxHeight": "600px",  # Set a max height to ensure the table doesn't get too large
            "overflowY": "auto"    # Add vertical scrolling
        }
    )

    return table_container

def create_editable_csv_preview_table(preview_data, row_results=None, id_prefix="csv-edit"):
    """
    Creates an editable table to preview and edit CSV data with validation status.

    Args:
        preview_data (list): List of dictionaries representing CSV rows
        row_results (list, optional): Validation results for each row
        id_prefix (str): Prefix for the input IDs

    Returns:
        dash component: A table component showing the CSV preview with editable cells for rows with errors
    """
    if not preview_data:
        return html.Div("No data to preview")

    # Create header
    columns = list(preview_data[0].keys())

    # Move 'Row Number' to the beginning if it exists
    if 'Row Number' in columns:
        columns.remove('Row Number')
        display_columns = ['Row Number'] + columns
    else:
        display_columns = columns

    header = html.Thead(html.Tr([html.Th("Status")] + [html.Th(col) for col in display_columns] + [html.Th("Actions")]))

    # Create rows
    rows = []
    for i, row in enumerate(preview_data):
        # Determine row status
        status_icon = html.I(className="fas fa-check-circle text-success")
        row_class = ""
        tooltip_text = "Valid"
        is_valid = True

        # Get the actual row number from the data if available, otherwise use the index
        row_number = row.get('Row Number', i + 2)  # +2 for header and 0-indexing

        # Find the corresponding validation result
        result = None
        if row_results:
            # Try to find by row number first
            for r in row_results:
                if r['row_number'] == row_number:
                    result = r
                    break

            # If not found and we're within range, use the index
            if result is None and i < len(row_results):
                result = row_results[i]

        # Update status based on validation result
        if result:
            is_valid = result['is_valid']
            if not is_valid:
                status_icon = html.I(className="fas fa-exclamation-circle text-danger")
                row_class = "table-danger"
                tooltip_text = ", ".join(result['issues'])

        # Create status cell with tooltip
        status_cell = html.Td(
            [
                html.Div(
                    status_icon,
                    id=f"{id_prefix}-row-status-{i}"
                ),
                dbc.Tooltip(
                    tooltip_text,
                    target=f"{id_prefix}-row-status-{i}",
                    placement="top"
                )
            ]
        )

        # Create row cells
        cells = [status_cell]

        # Add cells in the correct order
        for col in display_columns:
            cell_value = row.get(col, "")

            # Don't make Row Number editable
            if col == 'Row Number' or is_valid:
                cell = html.Td(str(cell_value))
            else:
                # Make cells editable for rows with errors
                input_id = {"type": "csv-edit-input", "index": i, "column": col.replace(" ", "_")}
                cell = html.Td(
                    dbc.Input(
                        id=input_id,
                        type="text",
                        value=str(cell_value),
                        className="form-control-sm"
                    )
                )

            cells.append(cell)

        # Add delete button
        delete_button = dbc.Button(
            html.I(className="fas fa-trash"),
            id={"type": "csv-delete-row", "index": i},
            color="danger",
            size="sm",
            className="me-1",
            title="Delete Row"
        )

        cells.append(html.Td(delete_button))

        # Add row to rows list
        rows.append(html.Tr(cells, className=row_class))

    # Create table body
    body = html.Tbody(rows)

    # Create table with scrollable container for large datasets
    table_container = html.Div(
        dbc.Table(
            [header, body],
            bordered=True,
            hover=True,
            responsive=True,
            striped=True,
            className="csv-preview-table"
        ),
        style={
            "maxHeight": "600px",  # Set a max height to ensure the table doesn't get too large
            "overflowY": "auto"    # Add vertical scrolling
        }
    )

    return table_container

def create_validation_summary(validation_results):
    """
    Creates a summary component for CSV validation results.

    Args:
        validation_results (dict): The validation results

    Returns:
        dash component: A component showing validation summary
    """
    if not validation_results:
        return html.Div()

    # Create summary card
    card_color = "success" if validation_results['is_valid'] else "warning"
    card_icon = "check-circle" if validation_results['is_valid'] else "exclamation-triangle"

    # Check if we're showing a subset of rows
    showing_subset_message = ""
    if validation_results.get('showing_subset', False):
        if validation_results.get('has_errors', False):
            showing_subset_message = html.P([
                html.I(className="fas fa-info-circle me-2"),
                "Note: Only showing a subset of rows including all errors and surrounding context. Toggle 'Show all rows' to see the complete file."
            ], className="text-info mt-2")
        else:
            showing_subset_message = html.P([
                html.I(className="fas fa-info-circle me-2"),
                "Note: Only showing a subset of rows from the beginning and end of the file. Toggle 'Show all rows' to see the complete file."
            ], className="text-info mt-2")

    summary = dbc.Card(
        dbc.CardBody([
            html.H5([
                html.I(className=f"fas fa-{card_icon} me-2"),
                "Validation Summary"
            ], className=f"text-{card_color}"),
            html.P([
                f"Total rows: {validation_results['total_rows']}",
                html.Br(),
                f"Valid rows: {validation_results['valid_rows']}",
                html.Br(),
                f"Invalid rows: {validation_results['invalid_rows']}"
            ]),
            # Show message about subset of rows if applicable
            showing_subset_message,
            # Show column issues if any
            html.Div([
                html.H6("Column Issues:"),
                html.Ul([html.Li(issue) for issue in validation_results['column_issues']])
            ]) if validation_results['column_issues'] else html.Div(),
            # Show general issues if any
            html.Div([
                html.H6("General Issues:"),
                html.Ul([html.Li(issue) for issue in validation_results['general_issues']])
            ]) if validation_results['general_issues'] else html.Div(),
        ]),
        color=card_color,
        outline=True,
        className="mb-3"
    )

    return summary

# --- Add/Edit Biomarker Modal Structure ---
biomarker_modal = dmc.Modal(
    title=dmc.Text(id="biomarker-modal-title", fw=700, size="lg"),
    children=[
        # Hidden input to store the ID of the biomarker being edited (or None for add)
        dcc.Store(id='biomarker-edit-id-store', data=None),

        # Name input
        dmc.Grid(
            [
                dmc.GridCol(dmc.Text("Name:", fw=500), span=3),
                dmc.GridCol(
                    dmc.TextInput(
                        id="biomarker-modal-name",
                        placeholder="e.g., Blood Glucose"
                    ),
                    span=9
                )
            ],
            mb="md"
        ),

        # Unit input
        dmc.Grid(
            [
                dmc.GridCol(dmc.Text("Unit:", fw=500), span=3),
                dmc.GridCol(
                    dmc.TextInput(
                        id="biomarker-modal-unit",
                        placeholder="e.g., mg/dL"
                    ),
                    span=9
                )
            ],
            mb="md"
        ),

        # Category input
        dmc.Grid(
            [
                dmc.GridCol(dmc.Text("Category:", fw=500), span=3),
                dmc.GridCol(
                    dmc.TextInput(
                        id="biomarker-modal-category",
                        placeholder="(Optional) e.g., Blood Sugar"
                    ),
                    span=9
                )
            ],
            mb="md"
        ),

        # Error message area
        dmc.Text(id="biomarker-modal-error-message", c="red", mt="md"),

        # Footer with buttons
        dmc.Group(
            [
                dmc.Button(
                    [html.I(className="fas fa-save me-2"), "Save"],
                    id="biomarker-modal-save-button",
                    color="blue",
                    variant="filled",
                    className="settings-btn-primary",
                    style={
                        "background": "linear-gradient(135deg, #007bff 0%, #0056b3 100%)",
                        "boxShadow": "0 4px 10px rgba(0, 123, 255, 0.2)",
                        "border": "none",
                        "fontWeight": "500"
                    },
                    n_clicks=0
                ),
                dmc.Button(
                    [html.I(className="fas fa-times me-2"), "Cancel"],
                    id="biomarker-modal-cancel-button",
                    variant="outline",
                    color="gray",
                    n_clicks=0
                )
            ],
            justify="flex-end",
            mt="xl"
        )
    ],
    id="biomarker-modal",
    opened=False,
    size="lg",
    transitionProps={"duration": 300},
    overlayProps={"blur": 3},
)

# --- Biomarker Card Component ---
def create_biomarker_card(biomarker, readings=None, reference_range=None):
    """
    Creates a biomarker card component similar to WellnessFX style.

    Args:
        biomarker (dict): Biomarker information (id, name, unit, category)
        readings (list, optional): List of readings for this biomarker
        reference_range (dict, optional): Reference range information

    Returns:
        dash_bootstrap_components.Card: A card component displaying the biomarker information
    """
    # Get the latest reading if available
    latest_reading = None
    if readings and len(readings) > 0:
        df_readings = pd.DataFrame(readings)
        latest_reading = df_readings.iloc[-1].to_dict()

    # Get the value and determine if it's in range
    value = latest_reading.get('value') if latest_reading else None
    in_range = None

    if value is not None and reference_range is not None:
        range_type = reference_range.get('range_type')
        lower_bound = reference_range.get('lower_bound')
        upper_bound = reference_range.get('upper_bound')

        if range_type == 'below':
            in_range = value < upper_bound
        elif range_type == 'above':
            in_range = value > lower_bound
        elif range_type == 'between':
            in_range = lower_bound <= value <= upper_bound

    # Set color based on range
    color = "success" if in_range else "danger" if in_range is not None else "secondary"

    # Create the visual indicator
    indicator = create_range_indicator(value, reference_range) if value is not None and reference_range is not None else None

    # Format the value with appropriate precision
    if value is not None:
        if isinstance(value, float):
            # For very small numbers (scientific notation)
            if abs(value) < 0.01:
                # Format as scientific notation but with HTML for better presentation
                base, exponent = f"{value:.2e}".split('e')
                # Remove leading + and convert to proper format
                exponent = exponent.replace('+', '')
                # Create HTML with superscript for exponent
                formatted_value = html.Span([
                    html.Span(base, className="formatted-number"),
                    html.Span([
                        "×10",
                        html.Sup(exponent)
                    ], className="scientific-notation")
                ])
            # For large numbers (over 1000)
            elif abs(value) >= 1000:
                # Format with commas for thousands separator
                formatted_value = f"{value:,.2f}"
            # For zero values, show as plain 0.00
            elif abs(value) < 0.000001:
                formatted_value = "0.00"
            # For normal range values
            else:
                formatted_value = f"{value:.2f}"  # 2 decimal places
        else:
            formatted_value = str(value)
    else:
        formatted_value = "No data"

    # Format the timestamp
    timestamp_text = ""
    if latest_reading and 'timestamp' in latest_reading:
        # Extract just the date part (first 10 characters of ISO format)
        timestamp_text = f"Last updated: {latest_reading['timestamp'][:10]}"

    # Create a simple range indicator instead of a sparkline graph
    sparkline = None
    risk_indicator = None

    # Create a simple range indicator if we have a reference range
    if reference_range is not None and value is not None:
        range_type = reference_range.get('range_type')
        lower_bound = reference_range.get('lower_bound')
        upper_bound = reference_range.get('upper_bound')

        # Determine the color for the risk indicator
        risk_color = "gray"  # Default color

        if range_type == 'below' and upper_bound is not None:
            if value < upper_bound:
                risk_color = "green"
            else:
                risk_color = "red"
        elif range_type == 'above' and lower_bound is not None:
            if value > lower_bound:
                risk_color = "green"
            else:
                risk_color = "red"
        elif range_type == 'between' and lower_bound is not None and upper_bound is not None:
            if value < lower_bound:
                risk_color = "red"
            elif value > upper_bound:
                risk_color = "red"
            else:
                risk_color = "orange"

        # Create the risk indicator
        risk_indicator = html.Div(
            className="risk-indicator",
            style={
                "background-color": risk_color,
            }
        )

        # If we have readings, create an Altair chart
        if readings and len(readings) > 0:
            # Create an Altair chart with full features
            chart = create_sparkline_chart(readings, reference_range)

            # Create a container for the chart
            sparkline = html.Div([
                # Embed the Altair chart
                embed_altair_chart(chart)
                # No need for separate reference range labels as they're now part of the chart
            ], className="sparkline-graph")

    # Create the card header with biomarker name and unit only
    header = dmc.CardSection(
        dmc.Group([
            dmc.Group([
                dmc.Text(biomarker['name'], fw=700, size="lg"),
                dmc.Text(f"({biomarker['unit']})", c="dimmed", size="sm")
            ], gap="xs")
        ], justify="flex-start"),
        withBorder=True,
        py="sm",
        px="md"
    )

    # Create the card body with value and timestamp
    body_content = [
        html.H3(formatted_value, className=f"text-{color} mb-1")  # Reduced margin
    ]

    # Add timestamp text
    if timestamp_text:
        body_content.append(html.P(timestamp_text, className="text-muted small mb-1"))  # Reduced margin

    # Create the card body with position relative for the risk indicator
    body = dmc.CardSection(
        body_content,
        p="xs",  # Reduced padding
        withBorder=False,
        style={"position": "relative"}
    )

    # Add the sparkline as the main content - it will now take up most of the card
    if sparkline:
        body.children.append(sparkline)
    else:
        # Add a placeholder div to maintain consistent height when there's no graph
        placeholder = html.Div(
            style={
                "height": "180px",  # Same height as the sparkline graph
                "width": "100%",
                "marginTop": "10px",
                "marginBottom": "10px"
            }
        )
        body.children.append(placeholder)

    # Add the risk indicator to the card body if available
    if risk_indicator:
        body.children.append(risk_indicator)

    # Add action buttons at the bottom of the card, after the sparkline
    action_buttons = dmc.Group([
        # View Readings button with eye icon
        dmc.Tooltip(
            label="View Readings",
            position="top",
            withArrow=True,
            children=dmc.ActionIcon(
                html.I(className="fas fa-eye"),
                id={'type': 'view-readings-button', 'index': biomarker['id']},
                color="gray",
                variant="light",
                size="md",  # Slightly smaller size
                radius="xl",
                style={
                    "boxShadow": "0 1px 3px rgba(0,0,0,0.1)",
                    "transition": "all 0.2s ease",
                },
                className="action-icon-hover"
            )
        ),
        # Add Reading button with plus icon
        dmc.Tooltip(
            label="Add Reading",
            position="top",
            withArrow=True,
            children=dmc.ActionIcon(
                html.I(className="fas fa-plus"),
                id={'type': 'add-reading-button', 'index': biomarker['id']},
                color="blue",
                variant="filled",
                size="md",  # Slightly smaller size
                radius="xl",
                style={
                    "boxShadow": "0 2px 4px rgba(0,0,0,0.2)",
                    "transition": "all 0.2s ease",
                },
                className="action-icon-hover"
            )
        )
    ], justify="center", mt="xs", mb="xs")

    body.children.append(action_buttons)

    # Create the card
    card = dmc.Card(
        [header, body],
        shadow="md",
        radius="lg",
        withBorder=True,
        p="xs",
        style={"height": "100%"},
        className="biomarker-card"
    )

    return card

def create_range_indicator(value, reference_range):
    """
    Creates a visual indicator showing where a value falls within a reference range.

    Args:
        value (float): The value to display
        reference_range (dict): Reference range information

    Returns:
        html.Div: A div containing the visual indicator
    """
    range_type = reference_range.get('range_type')
    lower_bound = reference_range.get('lower_bound')
    upper_bound = reference_range.get('upper_bound')

    # Default indicator for when we can't create a proper visualization
    if not range_type or (range_type == 'below' and upper_bound is None) or (range_type == 'above' and lower_bound is None) or (range_type == 'between' and (lower_bound is None or upper_bound is None)):
        return html.Div()

    # Create a horizontal bar with a marker
    if range_type == 'below':
        # For 'below' type, we show a bar from 0 to upper_bound with the marker at value
        # Calculate position percentage (capped at 100%)
        position_pct = min(100, (value / upper_bound) * 100)

        # Create the indicator
        indicator = html.Div([
            html.Div([
                # Red zone (above upper_bound)
                html.Div(className="bg-danger", style={"height": "100%", "width": "100%"}),
                # Green zone (below upper_bound)
                html.Div(className="bg-success", style={"height": "100%", "width": "100%", "position": "absolute", "top": 0, "left": 0, "right": f"{100-position_pct}%"}),
                # Marker
                html.Div(className="marker", style={"left": f"{position_pct}%"})
            ], className="range-bar"),
            # Labels
            html.Div([
                html.Span("0", className="small text-muted"),
                html.Span(f"{upper_bound}", className="small text-muted")
            ], className="d-flex justify-content-between mt-1")
        ], className="range-indicator")

    elif range_type == 'above':
        # For 'above' type, we show a bar from lower_bound to 2*lower_bound with the marker at value
        # Calculate position percentage (capped at 100%)
        max_value = lower_bound * 2  # Use 2x lower_bound as the max for visualization
        position_pct = min(100, ((value - lower_bound) / (max_value - lower_bound)) * 100)

        # Create the indicator
        indicator = html.Div([
            html.Div([
                # Red zone (below lower_bound)
                html.Div(className="bg-danger", style={"height": "100%", "width": "100%"}),
                # Green zone (above lower_bound)
                html.Div(className="bg-success", style={"height": "100%", "width": "100%", "position": "absolute", "top": 0, "left": f"{0}%", "right": f"{100-position_pct}%"}),
                # Marker
                html.Div(className="marker", style={"left": f"{position_pct}%"})
            ], className="range-bar"),
            # Labels
            html.Div([
                html.Span(f"{lower_bound}", className="small text-muted"),
                html.Span(f"{max_value}", className="small text-muted")
            ], className="d-flex justify-content-between mt-1")
        ], className="range-indicator")

    elif range_type == 'between':
        # For 'between' type, we show a bar from lower_bound to upper_bound with the marker at value
        # Calculate position percentage
        range_width = upper_bound - lower_bound
        position_pct = ((value - lower_bound) / range_width) * 100
        position_pct = max(0, min(100, position_pct))  # Clamp between 0-100%

        # Create the indicator
        indicator = html.Div([
            html.Div([
                # Red zones (outside range)
                html.Div(className="bg-danger", style={"height": "100%", "width": "100%"}),
                # Green zone (inside range)
                html.Div(className="bg-success", style={"height": "100%", "position": "absolute", "top": 0, "left": "0%", "width": "100%"}),
                # Marker
                html.Div(className="marker", style={"left": f"{position_pct}%"})
            ], className="range-bar"),
            # Labels
            html.Div([
                html.Span(f"{lower_bound}", className="small text-muted"),
                html.Span(f"{upper_bound}", className="small text-muted")
            ], className="d-flex justify-content-between mt-1")
        ], className="range-indicator")

    else:
        # Fallback for unknown range types
        indicator = html.Div()

    return indicator

# --- Data Entry Modal Structure ---
add_reading_modal = dmc.Modal(
    title=dmc.Group([
        html.I(className="fas fa-plus-circle me-2", style={"color": "var(--mantine-color-blue-6)"}),
        dmc.Text("Add New Biomarker Reading", fw=700, size="lg")
    ]),
    styles={
        "modal": {
            "borderRadius": "16px",
            "boxShadow": "0 10px 40px rgba(0, 0, 0, 0.15)",
        },
        "header": {
            "backgroundColor": "var(--mantine-color-gray-0)",
            "borderBottom": "1px solid var(--mantine-color-gray-2)",
            "padding": "20px 24px",
        },
        "body": {
            "padding": "24px",
        }
    },
    children=[
        # Biomarker dropdown
        dmc.Grid(
            [
                dmc.GridCol(dmc.Text("Biomarker:", fw=500), span=3),
                dmc.GridCol(
                    dcc.Dropdown(
                        id="modal-biomarker-dropdown",
                        placeholder="Select Biomarker...",
                        className="apple-dropdown"
                    ),
                    span=9
                )
            ],
            mb="md"
        ),

        # Date and time inputs
        dmc.Grid(
            [
                dmc.GridCol(dmc.Text("Date & Time:", fw=500), span=3),
                dmc.GridCol([
                    # Keep the original input but hide it for backward compatibility
                    html.Div(
                        dcc.Input(
                            id="modal-datetime-input",
                            type="text",
                            placeholder="YYYY-MM-DD HH:MM:SS"
                        ),
                        style={"display": "none"}
                    ),
                    # Date picker
                    dmc.Text("Date:", fw=500, mb="xs"),
                    dmc.DatePickerInput(
                        id="modal-date-picker",
                        valueFormat="YYYY-MM-DD",
                        placeholder="Select date",
                        clearable=True,
                        mb="md",
                        w="100%"
                    ),
                    # Time picker
                    dmc.Text("Time:", fw=500, mb="xs"),
                    dmc.TimeInput(
                        id="modal-time-picker",
                        withSeconds=False,
                        w="100%"
                    ),
                    # Hidden store to combine date and time
                    dcc.Store(id="modal-datetime-combined", data=None)
                ], span=9)
            ],
            mb="md"
        ),

        # Value input
        dmc.Grid(
            [
                dmc.GridCol(dmc.Text("Value:", fw=500), span=3),
                dmc.GridCol([
                    dmc.Group([
                        dmc.NumberInput(
                            id="modal-value-input",
                            placeholder="Enter value",
                            w="70%"
                        ),
                        dmc.Text(id="modal-unit-display", w="30%")
                    ], grow=True)
                ], span=9)
            ],
            mb="md"
        ),

        # Error message area
        dmc.Text(id="modal-error-message", c="red", mt="md"),

        # Footer with buttons
        dmc.Group(
            [
                dmc.Button(
                    "Save",
                    id="modal-save-button",
                    color="blue",
                    variant="filled",
                    n_clicks=0,
                    radius="md",
                    size="md",
                    leftSection=html.I(className="fas fa-check")
                ),
                dmc.Button(
                    "Cancel",
                    id="modal-cancel-button",
                    variant="outline",
                    color="gray",
                    n_clicks=0,
                    radius="md",
                    size="md"
                )
            ],
            justify="flex-end",
            mt="xl"
        )
    ],
    id="add-reading-modal",
    opened=False,
    size="lg",
    transitionProps={"duration": 300, "transition": "slide-up"},
    overlayProps={"blur": 5, "opacity": 0.55},
    centered=True,
    shadow="xl"
)
