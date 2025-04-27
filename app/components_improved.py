"""
Improved version of the create_sparkline_chart function with Apple-style design.
This file contains only the improved function to be copied into components.py.
"""

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

    # Extract min and max values for better scaling with more padding for better visualization
    min_value = df['value'].min() * 0.85  # Add 15% padding below
    max_value = df['value'].max() * 1.15  # Add 15% padding above

    # Ensure min_value is not negative for values that should be positive
    if min_value < 0 and df['value'].min() >= 0:
        min_value = 0

    # For a single reading, we need to create a synthetic second point for the chart
    if len(df) == 1:
        # Get the single reading
        single_timestamp = df['timestamp'].iloc[0]

        # Create a synthetic second point 30 days before with the same value
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

        # Adjust min and max values to include reference range
        if lower_bound is not None and lower_bound < min_value:
            min_value = lower_bound * 0.85
        if upper_bound is not None and upper_bound > max_value:
            max_value = upper_bound * 1.15

    # Create background layers for reference ranges with subtle gradients
    background_layers = []
    if reference_range:
        if range_type == 'between' and lower_bound is not None and upper_bound is not None:
            # Normal range (between lower and upper bounds) - subtle green gradient
            background_layers.append(
                alt.Chart(pd.DataFrame({
                    'y1': [lower_bound],
                    'y2': [upper_bound]
                })).mark_area(
                    color=APPLE_COLORS['green'],
                    opacity=0.15
                ).encode(
                    y='y1:Q',
                    y2='y2:Q'
                )
            )

            # Below range - subtle red gradient
            background_layers.append(
                alt.Chart(pd.DataFrame({
                    'y1': [min_value],
                    'y2': [lower_bound]
                })).mark_area(
                    color=APPLE_COLORS['red'],
                    opacity=0.15
                ).encode(
                    y='y1:Q',
                    y2='y2:Q'
                )
            )

            # Above range - subtle red gradient
            background_layers.append(
                alt.Chart(pd.DataFrame({
                    'y1': [upper_bound],
                    'y2': [max_value]
                })).mark_area(
                    color=APPLE_COLORS['red'],
                    opacity=0.15
                ).encode(
                    y='y1:Q',
                    y2='y2:Q'
                )
            )
        elif range_type == 'below' and upper_bound is not None:
            # Normal range (below upper_bound) - subtle green gradient
            background_layers.append(
                alt.Chart(pd.DataFrame({
                    'y1': [min_value],
                    'y2': [upper_bound]
                })).mark_area(
                    color=APPLE_COLORS['green'],
                    opacity=0.15
                ).encode(
                    y='y1:Q',
                    y2='y2:Q'
                )
            )

            # Above range - subtle red gradient
            background_layers.append(
                alt.Chart(pd.DataFrame({
                    'y1': [upper_bound],
                    'y2': [max_value]
                })).mark_area(
                    color=APPLE_COLORS['red'],
                    opacity=0.15
                ).encode(
                    y='y1:Q',
                    y2='y2:Q'
                )
            )
        elif range_type == 'above' and lower_bound is not None:
            # Below range - subtle red gradient
            background_layers.append(
                alt.Chart(pd.DataFrame({
                    'y1': [min_value],
                    'y2': [lower_bound]
                })).mark_area(
                    color=APPLE_COLORS['red'],
                    opacity=0.15
                ).encode(
                    y='y1:Q',
                    y2='y2:Q'
                )
            )

            # Normal range (above lower_bound) - subtle green gradient
            background_layers.append(
                alt.Chart(pd.DataFrame({
                    'y1': [lower_bound],
                    'y2': [max_value]
                })).mark_area(
                    color=APPLE_COLORS['green'],
                    opacity=0.15
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
                    format='%b %Y',  # Format as "Apr 2018"
                    labelAngle=-45,
                    title=None,
                    labelColor=APPLE_COLORS['gray'],
                    labelFont='SF Pro Display, -apple-system, BlinkMacSystemFont, sans-serif',
                    labelFontSize=10,
                    tickColor=APPLE_COLORS['light_gray'],
                    domainColor=APPLE_COLORS['light_gray']
                )),
        y=alt.Y('value:Q',
                scale=alt.Scale(domain=[min_value, max_value]),
                axis=alt.Axis(
                    title=None,
                    labelColor=APPLE_COLORS['gray'],
                    labelFont='SF Pro Display, -apple-system, BlinkMacSystemFont, sans-serif',
                    labelFontSize=10,
                    tickColor=APPLE_COLORS['light_gray'],
                    domainColor=APPLE_COLORS['light_gray'],
                    grid=True,
                    gridColor=APPLE_COLORS['light_gray'],
                    gridOpacity=0.3,
                    gridDash=[2, 2]
                )),
        tooltip=[
            alt.Tooltip('formatted_date:N', title='Date'),
            alt.Tooltip('formatted_value:N', title='Value')
        ]
    )

    # Create the line chart with smooth interpolation
    line = base.mark_line(
        color=APPLE_COLORS['blue'],
        strokeWidth=2,
        interpolate='monotone',  # Smooth, curved lines
        strokeOpacity=0.8
    )

    # Add points at each data point with interactive hover effects
    points = base.mark_point(
        color=APPLE_COLORS['blue'],
        size=80,  # Larger for better touch targets
        filled=True,
        opacity=0.8,
        shape='circle'
    ).encode(
        size=alt.value(80),  # Default size
        opacity=alt.value(0.8)  # Default opacity
    ).add_selection(
        alt.selection_single(
            on='mouseover',
            nearest=True,
            fields=['timestamp'],
            empty='none'
        )
    )

    # Add hover effect for points
    hover_points = base.mark_point(
        color=APPLE_COLORS['blue'],
        filled=True,
        shape='circle'
    ).encode(
        size=alt.condition(
            alt.datum.timestamp == alt.selection_single(nearest=True, on='mouseover', fields=['timestamp']),
            alt.value(120),  # Larger size on hover
            alt.value(0)  # Hidden when not hovered
        ),
        opacity=alt.condition(
            alt.datum.timestamp == alt.selection_single(nearest=True, on='mouseover', fields=['timestamp']),
            alt.value(1),  # Full opacity on hover
            alt.value(0)  # Hidden when not hovered
        ),
        stroke=alt.value('white'),
        strokeWidth=alt.value(2)
    ).add_selection(
        alt.selection_single(
            on='mouseover',
            nearest=True,
            fields=['timestamp'],
            empty='none'
        )
    )

    # Add text labels with values only on hover for cleaner look
    text = base.mark_text(
        align='center',
        baseline='bottom',
        dy=-10,  # Offset above the point
        fontSize=12,
        fontWeight='bold',
        font='SF Pro Display, -apple-system, BlinkMacSystemFont, sans-serif',
        color=APPLE_COLORS['dark_gray']
    ).encode(
        text=alt.Text('value:Q', format='.1f'),  # Format with 1 decimal place
        opacity=alt.condition(
            alt.datum.timestamp == alt.selection_single(nearest=True, on='mouseover', fields=['timestamp']),
            alt.value(1),  # Show text on hover
            alt.value(0)  # Hide text when not hovered
        )
    ).add_selection(
        alt.selection_single(
            on='mouseover',
            nearest=True,
            fields=['timestamp'],
            empty='none'
        )
    )

    # Add reference lines if provided - using dotted lines for better visibility
    reference_layers = []
    if reference_range:
        if lower_bound is not None:
            reference_layers.append(
                alt.Chart(pd.DataFrame({'y': [lower_bound]})).mark_rule(
                    color=APPLE_COLORS['orange'],
                    strokeDash=[4, 2],
                    strokeWidth=1,
                    opacity=0.7
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
                    strokeWidth=1,
                    opacity=0.7
                ).encode(
                    y='y:Q',
                    tooltip=alt.Tooltip('y:Q', title='Upper Bound', format='.2f')
                )
            )

    # Combine all layers
    chart = alt.layer(*background_layers) if background_layers else alt.Chart()
    for layer in reference_layers:
        chart += layer
    chart += line + points + hover_points + text

    # Configure the chart appearance for a clean, Apple-style look
    chart = chart.configure_view(
        strokeWidth=0,
        strokeOpacity=0,
        fill=APPLE_COLORS['background'],
        fillOpacity=0.1,
        cornerRadius=8  # Rounded corners for Apple-style
    ).properties(
        width='container',  # Responsive width
        height=180,  # Fixed height to prevent scrollbar
        usermeta={"embedOptions": {"actions": False}}  # Disable the three-dot menu
    ).configure_axis(
        labelFont='SF Pro Display, -apple-system, BlinkMacSystemFont, sans-serif',
        titleFont='SF Pro Display, -apple-system, BlinkMacSystemFont, sans-serif',
        labelFontSize=10,
        titleFontSize=12
    ).configure_legend(
        labelFont='SF Pro Display, -apple-system, BlinkMacSystemFont, sans-serif',
        titleFont='SF Pro Display, -apple-system, BlinkMacSystemFont, sans-serif',
        labelFontSize=10,
        titleFontSize=12
    ).configure_title(
        font='SF Pro Display, -apple-system, BlinkMacSystemFont, sans-serif',
        fontSize=14,
        fontWeight='bold'
    )

    return chart
