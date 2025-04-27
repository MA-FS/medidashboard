"""
Test script to verify that the chart implementation works correctly.
"""

import pandas as pd
import altair as alt
from datetime import datetime, timedelta
import dash
from dash import dcc, html
import dash_bootstrap_components as dbc

# Create sample data
def create_sample_data():
    # Create dates for the last 6 months
    end_date = datetime.now()
    dates = [end_date - timedelta(days=30*i) for i in range(6)]
    
    # Create sample readings
    readings = []
    for i, date in enumerate(dates):
        readings.append({
            'id': i+1,
            'timestamp': date.isoformat(),
            'value': 5.5 + i * 0.2  # Increasing values
        })
    
    return readings

# Create a simplified version of the chart function
def create_test_chart(readings):
    # Convert readings to DataFrame
    df = pd.DataFrame(readings)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df = df.sort_values('timestamp')
    
    # Calculate min and max values
    min_value = df['value'].min() * 0.9
    max_value = df['value'].max() * 1.1
    
    # Add formatted date and value for tooltips
    df['formatted_date'] = df['timestamp'].dt.strftime('%b %d, %Y')
    df['formatted_value'] = df['value'].apply(lambda x: f"{x:.2f}")
    
    # Create a single hover selection
    hover = alt.selection_single(
        on='mouseover',
        nearest=True,
        fields=['timestamp'],
        empty='none',
        name='hover'
    )
    
    # Create the base chart
    base = alt.Chart(df).encode(
        x=alt.X('timestamp:T', axis=alt.Axis(format='%b %Y', labelAngle=-45, title=None)),
        y=alt.Y('value:Q', scale=alt.Scale(domain=[min_value, max_value]), axis=alt.Axis(title=None)),
        tooltip=['formatted_date:N', 'formatted_value:N']
    )
    
    # Create the line chart
    line = base.mark_line(color='#007AFF', strokeWidth=2, interpolate='monotone')
    
    # Add points
    points = base.mark_point(color='#007AFF', filled=True, shape='circle').encode(
        size=alt.condition(hover, alt.value(120), alt.value(80)),
        opacity=alt.condition(hover, alt.value(1), alt.value(0.8))
    ).add_selection(hover)
    
    # Add text labels
    text = base.mark_text(
        align='center',
        baseline='bottom',
        dy=-10,
        fontSize=12,
        fontWeight='bold',
        color='#3A3A3C'
    ).encode(
        text=alt.Text('value:Q', format='.1f'),
        opacity=alt.condition(hover, alt.value(1), alt.value(0))
    )
    
    # Combine layers
    chart = line + points + text
    
    # Configure the chart
    chart = chart.configure_view(
        strokeWidth=0,
        strokeOpacity=0
    ).properties(
        width=350,
        height=180
    )
    
    return chart

# Create a Dash app to display the chart
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# Generate sample data
sample_data = create_sample_data()

# Create the chart
chart = create_test_chart(sample_data)

# Convert chart to HTML
chart_html = chart.to_html(embed_options={'actions': False})

# Create the app layout
app.layout = dbc.Container([
    html.H1("Chart Test", className="mt-4 mb-4"),
    html.Div([
        html.H3("Sample Chart"),
        html.Iframe(
            srcDoc=chart_html,
            style={
                'border': 'none',
                'width': '100%',
                'height': '250px',
                'overflow': 'hidden'
            }
        )
    ], className="p-4 border rounded")
])

# Run the app
if __name__ == "__main__":
    app.run_server(debug=True)
