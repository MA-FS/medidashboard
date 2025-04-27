# Product Context: MediDashboard

## Problem Solved

Provides a private, user-controlled way to track personal medical biomarker data over time without relying on third-party cloud services. Enables visualization of trends for better health monitoring.

## How it Works

- Users define the specific biomarkers they want to track.
- They enter readings (value and timestamp) for these biomarkers through a simple web interface.
- The application displays interactive charts showing trends over time for each biomarker.
- Data is stored in a local SQLite file, managed entirely by the user.
- Backup and restore functionality allows users to safeguard and manage their data file.

## User Experience Goals

- **Intuitive & Simple:** Easy navigation, clear data entry, straightforward visualization.
- **Professional & Clean:** Design inspired by Apple's Human Interface Guidelines.
- **Responsive:** Adapts to different browser window sizes.
- **Secure & Private:** All data remains local to the user's machine.
- **Reliable:** Robust data storage and backup mechanisms. 