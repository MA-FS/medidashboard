
# Design Plan: Personal Medical Biomarker Dashboard (Web-Based)

## 1. Introduction

The objective is to design and develop a user-friendly, professional-looking, web-based application that runs locally on the user's computer. This application will allow the user to:

* Define and manage custom medical biomarkers (e.g., name, unit).
* Enter time-stamped values for these biomarkers.
* Visualize biomarker trends over time via an interactive dashboard.
* Securely store all data locally.
* Easily back up and restore the entire dataset.

The application will be accessible via a standard web browser on any operating system (Windows, macOS, Linux), ensuring cross-platform compatibility.

## 2. Technology Stack Selection

Based on the requirements for a web-based interface, cross-platform accessibility, ease of development (especially for data-centric applications), and local operation, the following technology stack is selected:

* **Web Framework:** `Dash` (by Plotly).¹ `Dash` is a Python framework specifically designed for building analytical web applications and interactive dashboards purely in Python.¹ It integrates seamlessly with Plotly for charting and runs a local web server (using Flask underneath), making the application accessible via `http://localhost` in a browser.¹ This avoids the need for separate complex frontend development while meeting the web-based requirement.
* **Charting Library:** `Plotly.py`.⁵ As the library `Dash` is built upon, `Plotly.py` provides a vast range of interactive, high-quality charts suitable for time-series data visualization.⁵ Its interactivity (zoom, pan, hover tooltips) is crucial for exploring biomarker trends.⁷
* **Database:** `SQLite`.⁸ `SQLite` is the ideal choice for local, single-user data storage. It's serverless, stores the entire database in a single file, requires zero configuration, and has excellent Python support.⁸ Its single-file nature greatly simplifies the backup and restore process.⁸
* **Programming Language:** `Python`. Leveraged by `Dash`, `Plotly.py`, and `SQLite` libraries, providing a unified development language.

## 3. Application Architecture

A simple layered architecture will be employed for maintainability:

* **Presentation Layer (UI):** Handled by `Dash` components (`dash_html_components`, `dash_core_components`). Defines the layout, widgets, forms, and charts displayed in the web browser.
* **Business Logic Layer (BLL):** Python functions and classes that handle data processing, calculations for trends (if any beyond simple plotting), managing biomarker definitions, and orchestrating data flow between the UI and the database.
* **Data Access Layer (DAL):** Python functions specifically interacting with the SQLite database using Python's built-in `sqlite3` module. This layer will handle all CRUD (Create, Read, Update, Delete) operations and the backup/restore logic.

## 4. Database Design (SQLite)

The SQLite database will be stored as a single file (e.g., `biomarkers.db`) in the user's local application data directory to ensure appropriate permissions and avoid clutter.¹² The schema will include at least two main tables:

* **Biomarkers Table:** Stores the definitions of the biomarkers the user wants to track.
    * `id` (INTEGER, PRIMARY KEY, AUTOINCREMENT)
    * `name` (TEXT, NOT NULL, UNIQUE) - e.g., "Blood Glucose", "Heart Rate"
    * `unit` (TEXT, NOT NULL) - e.g., "mmol/L", "bpm"
    * `category` (TEXT) - e.g., "Lipids", "Hormones"
* **Readings Table:** Stores the time-stamped values for each biomarker reading.
    * `id` (INTEGER, PRIMARY KEY, AUTOINCREMENT)
    * `biomarker_id` (INTEGER, NOT NULL, FOREIGN KEY REFERENCES Biomarkers(id))
    * `timestamp` (TEXT or INTEGER, NOT NULL) - Store as ISO 8601 string or Unix timestamp.
    * `value` (REAL, NOT NULL) - The numeric value of the reading.

Indexes will be created on `Readings.biomarker_id` and `Readings.timestamp` to optimize queries for trend visualization.

## 5. User Interface (UI) and User Experience (UX) Design

The design will prioritize simplicity, clarity, and ease of use, following established dashboard design principles.¹³

### Core Principles:

* **User-Focused:** Tailored for personal tracking and understanding trends.
* **Clarity:** Minimal clutter, ample whitespace, clear typography, consistent styling.¹⁶
* **Visual Hierarchy:** Design to mimic apple design and follow the apple human interface guidelines. Most important information (current status, recent trends) presented prominently.¹⁷
* **Actionable:** Charts should clearly show trends and allow interaction.¹⁸

### Main Dashboard Page:

* **Layout:** A widget-based grid layout. Each widget represents a tracked biomarker. A category column down the side of the page will determine what widgets are shown.
* **Widgets:** Each biomarker widget will display:
    * Biomarker Name and Unit.
    * An interactive Plotly line chart showing the trend over time.⁵ Users can zoom, pan, and hover over points to see exact values and dates.
    * The most recent value and date.
    * (Optional) Sparkline or simple summary statistics (e.g., average, min/max over a period).
* **Controls:** A prominent "Add New Reading" button. A link/button to navigate to the "Settings" page.

### Data Entry Form (Accessed via "Add New Reading"):

* A simple modal dialog or dedicated section.
* Dropdown list to select the Biomarker (populated from the `Biomarkers` table).
* Date and Time Picker for the timestamp.
* Numeric input field for the value. The associated unit for the selected biomarker will be displayed next to the input field for clarity.
* Input validation (e.g., ensure value is numeric, date is valid).²³
* Clear "Save" and "Cancel" buttons.

### Settings Page:

#### Navigation:
Accessible from the main dashboard.

#### Manage Biomarkers Section:
* A collapsible table displaying all defined biomarkers (Name, Unit).
* Buttons: "Add New Biomarker", "Edit" (per row), "Delete" (per row, with confirmation).
* Simple forms (modal or inline) for adding/editing biomarker definitions (Name, Unit fields).

#### Data Management Section:
* **Backup:** A button labeled "Backup Data (Download)". Clicking this triggers the backend to create a backup using the SQLite `.backup` command and initiates a browser download of the `.db` file.¹¹
* **Restore:** An "Upload Backup File" button/area. A clear warning message stating that restoring will overwrite all current data. Upon file selection and confirmation, the backend replaces the active database file with the uploaded one and reloads the application.²⁴

## 6. Core Features Implementation

* **Biomarker Definition Management:** Python functions in the DAL to perform `INSERT`, `UPDATE`, `DELETE` operations on the `Biomarkers` table in SQLite. BLL functions to handle the logic and interact with the UI components.
* **Data Recording:** Python function in the DAL to `INSERT` new records into the `Readings` table. BLL validates input and links the reading to the correct `biomarker_id`.
* **Trend Visualization:** Python functions in the DAL to query the `Readings` table for data points of a specific `biomarker_id` within a given time range, ordered by `timestamp`. BLL processes this data (if needed) and passes it to a `Plotly.py` function to generate the interactive line chart figure. This figure is embedded into a `Dash` `dcc.Graph` component on the dashboard.¹
* **Backup/Restore:**
    * **Backup:** A `Dash` callback triggered by the "Backup" button executes a Python function on the server. This function uses `sqlite3` to connect to the source database and execute the `.backup 'path/to/temporary_backup.db'` command.²⁴ The server then sends this `temporary_backup.db` file to the user's browser for download.
    * **Restore:** A `Dash` `dcc.Upload` component handles file upload. A callback receives the uploaded file. After user confirmation (via a modal), the callback closes existing database connections, replaces the current `biomarkers.db` file with the uploaded file, and then re-initializes the application or prompts the user to restart it.

## 7. Deployment and Access

* The application will be packaged with its Python dependencies (`Dash`, `Plotly`, etc.).
* The user will run a simple script (e.g., `run_dashboard.py`) or a bundled executable.
* This script starts the local `Dash`/`Flask` web server.
* The user accesses the application by opening their web browser and navigating to `http://localhost:8050` (or another specified port).³ No internet connection is required after initial setup.

## 8. Conclusion

This plan outlines the development of a robust, user-friendly, and secure personal medical biomarker tracking application. By leveraging the `Python` ecosystem with `Dash` for the web interface, `Plotly.py` for interactive visualizations, and `SQLite` for reliable local data storage and backup, the application will provide a seamless experience for users to monitor their health trends directly on their own computer, accessible from any operating system via a web browser.
