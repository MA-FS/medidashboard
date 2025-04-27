# System Patterns

## Architecture

A layered architecture will be used:
- **Presentation Layer (UI):** `Dash` components (`dash_html_components`, `dash_core_components`). Handles browser display.
- **Business Logic Layer (BLL):** Python functions/classes. Manages data processing, biomarker logic, UI-DB interaction.
- **Data Access Layer (DAL):** Python functions using `sqlite3` module. Handles all database CRUD and backup/restore operations.

## Key Technical Decisions

- **Local Execution:** Application runs entirely on the user's machine via a local web server.
- **Web Interface:** `Dash` provides the browser-based UI.
- **Local Database:** `SQLite` stores data in a single file (`biomarkers.db`).
- **Interactive Charts:** `Plotly.py` used for dashboard visualizations.

## Component Relationships

UI (Dash) <- BLL (Python Logic) -> DAL (SQLite Interface) -> `biomarkers.db`

## Design Patterns

- **Layered Architecture:** Separation of concerns (UI, Logic, Data).
- **Single File Database:** Simplifies data management and backup (SQLite).
- **Callback-Driven UI:** Dash uses callbacks to connect UI elements to backend Python functions. 