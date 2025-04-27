#!/usr/bin/env python3
"""
run.py - Main entry point to run the MediDashboard application

This script starts the MediDashboard web application and accepts
command-line arguments for configuration.

Usage:
    python run.py [options]

Options:
    --host HOST       Host to bind to (default: 127.0.0.1)
    --port PORT       Port to bind to (default: 8050)
    --debug           Enable debug mode (default: False)
    --network         Make accessible on the network (shortcut for --host 0.0.0.0)
    --help            Show this help message and exit
"""

import argparse
import sys
from app.app import app, server  # Import the app instance and server

def parse_arguments():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description='Run the MediDashboard application')
    parser.add_argument('--host', type=str, default='127.0.0.1',
                        help='Host to bind to (default: 127.0.0.1)')
    parser.add_argument('--port', type=int, default=8050,
                        help='Port to bind to (default: 8050)')
    parser.add_argument('--debug', action='store_true',
                        help='Enable debug mode')
    parser.add_argument('--network', action='store_true',
                        help='Make accessible on the network (shortcut for --host 0.0.0.0)')

    args = parser.parse_args()

    # Override host if --network is specified
    if args.network:
        args.host = '0.0.0.0'
        print("Network mode enabled. App will be accessible from other devices on the network.")

    return args

if __name__ == '__main__':
    # Show help if --help is specified
    if '--help' in sys.argv:
        print(__doc__)
        sys.exit(0)

    # Parse command-line arguments
    args = parse_arguments()

    print(f"Starting MediDashboard server on {args.host}:{args.port} (debug={args.debug})...")

    # Start the application
    app.run(debug=args.debug, host=args.host, port=args.port)  # Correct method for Dash 2.x+