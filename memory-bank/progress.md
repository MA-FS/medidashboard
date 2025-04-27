# Progress Tracking

## What Works

- **Project Setup:** Directory structure, Git repo, virtual environment, requirements file.
- **Database:** SQLite database (`biomarkers.db`) initialization script, table creation (Biomarkers, Readings), indexes.
- **Backend Logic (DAL/BLL):** 
    - Full CRUD operations for Biomarkers (tested).
    - Full CRUD operations for Readings (tested).
    - Querying readings by biomarker and date range (tested).
    - Basic input validation in BLL (tested).
- **Basic UI Structure:**
    - Multi-page Dash app setup (`app.py`).
    - Bootstrap styling integration.
    - Navigation bar (Dashboard/Settings).
    - Placeholder layouts for Dashboard and Settings pages.
    - Placeholder structure for Add Reading modal.
- **Settings Page - Biomarker List & CRUD:** 
    - Biomarker definitions fetched from BLL/DAL.
    - Table displaying Name, Unit, Category, and Edit/Delete buttons.
    - Add/Edit modal opens correctly for adding new or editing existing biomarkers.
    - Saving biomarkers via modal calls correct BLL function (add/update).
    - Deleting biomarkers via button triggers confirmation and calls correct BLL function.
    - Table refreshes automatically after successful add/edit/delete.
- **Add Biomarker Reading UI:**
    - Modal opens via Dashboard button.
    - Biomarker dropdown populated from database.
    - Unit display updates based on selection.
    - Save button calls BLL function with validation.
- **Dashboard Visualization:**
    - Category dropdown populated and filters displayed biomarkers.
    - Biomarker widgets display name, unit, latest reading, and Plotly line chart.
    - Charts update automatically when new readings are added.
    - Widgets arranged in columns.
- **Basic UI Tests:** Playwright environment setup, basic navigation tests pass.
- **Backup Functionality:** Button click generates timestamped DB backup file and triggers browser download.
- **Restore Functionality:** Uploading a valid `.db` backup file triggers confirmation, replaces the database, preserves biomarker definitions created since backup, displays status, and reloads the app.
- **Theme Switching:** Toggle in navbar switches between Bootstrap light and Vapor dark themes; choice persists locally.
- **Dashboard Configuration:** Settings tab allows users to select which biomarkers are visible on the dashboard; preference persists locally.
- **Chart Display Options:** Settings allow selecting a default time range (30d, 90d, 6m, 1y, All) which is applied to dashboard charts; preference persists locally.

## What's Left to Build (High-Level from implementation.md)

- **Phase 5 (Core Features):**
    - More comprehensive UI/Integration tests (Playwright - deferred).
    - (Optional) Reading Edit/Delete UI.
- **Phase 6 (Advanced Features):** UI tests for Backup/Restore (deferred).
- **Phase 7 (Configurability):** Dashboard layout (reorder - deferred), date format, E2E testing (deferred).
- **Phase 8 (Finalization):** Initial data seeding, UI polish, README, packaging, Memory Bank final update.

## Current Status

- Completed major configurability features.
- Evaluating Date/Time format option or moving to Phase 8.

## Known Issues

- Backup files created in `data/` directory are not automatically cleaned up.
- Temporary restore files (`restore_upload_*.db`) are cleaned up, but error handling could be more robust.
- No UI for editing or deleting individual readings yet.
- Time range filtering for dashboard charts not yet implemented.
- Reordering dashboard widgets not implemented. 