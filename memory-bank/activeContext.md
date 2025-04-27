# Active Context

## Current Focus

Consider Date/Time Formatting Options (Phase 7 - Low Priority) or move to Finalization (Phase 8).

## Recent Changes

- Completed Phase 2 (Project Setup & DB Initialization).
- Completed Phase 3 (Backend DAL/BLL Implementation & Unit Tests).
- Completed Phase 4 (Frontend UI Structure).
- Implemented full CRUD UI for Biomarker Definitions on Settings page.
- Implemented UI for Adding Biomarker Readings.
- Implemented Dashboard Visualization (Category Filter, Plotly Charts, Latest Reading Display).
- Added dashboard refresh trigger on new reading save.
- Set up basic Playwright testing environment and initial navigation tests.
- Implemented Backup functionality (DAL, BLL, UI callback, file download).
- Implemented Restore functionality (file upload, DB replace, biomarker merge, UI feedback, page reload).
- Implemented Theme Switching (Light/Dark) using ThemeSwitchAIO.
- Implemented Dashboard Config (Show/Hide Widgets via Settings checklist).
- Implemented Chart Display Options (Default Time Range selection in settings affecting dashboard charts).

## Next Steps

- Implement Date/Time Formatting Options (Low Priority)?
- Proceed to Phase 8 (Finalization - Initial Data Seeding, UI Polish, README).
- Implement deferred UI tests (Backup/Restore, Theme, Config, etc.).

## Active Decisions

- Using `dcc.Tabs` for Settings page navigation.
- Using `pandas` for table creation.
- Using Pattern-Matching IDs for Edit/Delete buttons.
- Using `dcc.Store` to trigger table refreshes.
- Using `dcc.ConfirmDialog` for delete confirmation.
- Using `dcc.Download` and `dcc.send_file` for backup download.
- Pausing further Playwright test implementation for now to focus on Backup/Restore.
- Using page reload via `dcc.Location` for simple app state refresh after restore.
- Using `dash-bootstrap-templates` and `ThemeSwitchAIO` for theme handling.
- Using `dbc.Checklist` and `dcc.Store` for widget visibility config.
- Using `dbc.RadioItems` and `dcc.Store` for time range preference. 