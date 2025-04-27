# MediDashboard

A personal health metrics tracking dashboard built with Python and Dash, featuring Apple-inspired design principles.

## Overview

MediDashboard is a web-based application that allows users to track and visualize their biomarker readings over time. It provides a clean, intuitive interface for managing health metrics and visualizing trends with interactive sparkline charts and color-coded reference ranges.

![MediDashboard Screenshot](docs/images/dashboard_screenshot.png)

## Features

- **Interactive Dashboard**: Visualize biomarker readings with Apple-style sparkline charts showing reference ranges
- **Biomarker Cards**: Compact, information-rich cards that expand into detailed modal views
- **Category-Based Organization**: Biomarkers organized by categories (Lipid Profile, Blood Sugar, etc.)
- **Reference Ranges**: Visual indicators showing when values are within or outside healthy ranges
- **Reading Management**: Add, edit, view, and delete readings with an intuitive interface
- **CSV Import/Export**: Easily import readings from CSV files or export your data for backup
- **Data Filtering**: Filter biomarkers by category with default view set to Lipid Profile
- **Time Range Selection**: View data for different time periods (30 days, 90 days, 6 months, 1 year, all)
- **Responsive Design**: Works on desktop and mobile devices with adaptive layout
- **Dark Mode Support**: Toggle between light and dark themes
- **Branding**: Subtle background logo that stays fixed while scrolling

## Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

### Setup

1. Clone the repository:
   ```
   git clone https://github.com/MA-FS/medi-dashboard.git
   cd medi-dashboard
   ```

2. Create and activate a virtual environment:
   ```
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Run the application:
   ```
   python run.py
   ```

   Or with custom options:
   ```
   python run.py --port 8051 --debug
   ```

5. Open your browser and navigate to:
   ```
   http://127.0.0.1:8050/
   ```


## Usage

### Adding Biomarkers

1. Navigate to the Settings page
2. Click "Add New Biomarker"
3. Enter the biomarker name, unit, and optional category
4. Click "Save"

### Recording Readings

1. From the Dashboard, click "Add Reading"
2. Select a biomarker from the dropdown
3. Enter the value and timestamp (defaults to current time)
4. Click "Save"

### Filtering and Customizing the Dashboard

- Use the category dropdown to filter biomarkers by category (defaults to Lipid Profile)
- Click on any biomarker card to view detailed information and history
- Use the "+" button on each biomarker card to quickly add a new reading
- Click the visibility icon next to biomarkers to show/hide them
- Use the time range selector to adjust the time period displayed

### Data Import and Export

- From the Settings page, go to the "Data Management" tab
- Click "Export Readings" to download all your data as a CSV file
- To import data, upload a CSV file in the correct format
- Use the "Download Template" button to get a sample CSV format
- Preview and validate your data before importing
- Option to skip duplicates during import

## Project Structure

```
medi-dashboard/
├── app/                    # Application code
│   ├── assets/             # Static assets
│   │   ├── custom.css      # Custom styling
│   │   └── logo.png        # Application logo
│   ├── callbacks/          # Dash callback modules
│   │   ├── biomarkers.py   # Biomarker management callbacks
│   │   ├── dashboard.py    # Dashboard callbacks
│   │   ├── readings.py     # Reading management callbacks
│   │   ├── readings_management.py # Reading management callbacks
│   │   ├── edit_readings.py # Edit reading callbacks
│   │   ├── routing.py      # URL routing callbacks
│   │   └── settings.py     # Settings page callbacks
│   ├── app_instance.py     # Dash app instance
│   ├── app.py              # Main application entry point
│   ├── bll.py              # Business Logic Layer
│   ├── components.py       # Reusable UI components
│   ├── dal.py              # Data Access Layer
│   ├── database_setup.py   # Database initialization
│   ├── layouts.py          # Page layouts
│   ├── utils.py            # Utility functions
│   └── validation.py       # Input validation
├── data/                   # Database and data files
├── docs/                   # Documentation
│   └── images/             # Screenshots and images
├── tests/                  # Test files
│   └── test_ui.py          # UI tests using Playwright
├── .gitignore              # Git ignore file
├── README.md               # This file
├── requirements.txt        # Python dependencies
└── run.py                  # Application entry point with command-line options
```

## Development

### Running Tests

The application includes UI tests using Playwright:

```
# Install Playwright browsers first
python -m playwright install

# Run the tests
python -m pytest
```

### Adding New Features

1. Fork the repository
2. Create a feature branch
3. Add your feature
4. Run tests
5. Submit a pull request

## Design Principles

MediDashboard follows Apple's Human Interface Guidelines for a clean, intuitive user experience:

- **Clarity**: Focus on essential content with clean, readable interfaces
- **Deference**: Fluid motion and crisp interface help users understand and interact
- **Depth**: Visual layers and realistic motion convey hierarchy and position

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- [Dash](https://dash.plotly.com/) - The web framework used
- [Altair](https://altair-viz.github.io/) - Declarative visualization library
- [Bootstrap](https://getbootstrap.com/) - Responsive UI components
- [SQLite](https://www.sqlite.org/) - Database engine
- [Playwright](https://playwright.dev/) - Testing framework
