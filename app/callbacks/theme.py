"""
theme.py - Callbacks for theme settings like dark mode toggle.
"""

from dash import Input, Output, callback, ctx

@callback(
    Output("color-scheme-store", "data"),
    Output("dark-mode-icon", "className"),
    Output("app-theme-provider", "theme"),
    Input("dark-mode-toggle", "n_clicks"),
    Input("color-scheme-store", "data")
)
def toggle_dark_mode(n_clicks, current_scheme):
    """Toggle between light and dark mode."""
    # Default to light mode if no data
    if current_scheme is None:
        current_scheme = "light"

    # Set the icon based on the current scheme
    icon_class = "fas fa-sun" if current_scheme == "dark" else "fas fa-moon"

    # Only toggle if the button was clicked
    if ctx.triggered_id == "dark-mode-toggle" and n_clicks:
        # Toggle between light and dark
        new_scheme = "dark" if current_scheme == "light" else "light"
        # Update icon based on new scheme
        icon_class = "fas fa-sun" if new_scheme == "dark" else "fas fa-moon"

        # Return the appropriate theme based on the new scheme
        if new_scheme == "dark":
            theme = {
                "colorScheme": "dark",
                "primaryColor": "blue",
                "colors": {
                    "dark": [
                        "#C1C2C5",  # Text color
                        "#A6A7AB",  # Secondary text
                        "#909296",  # Tertiary text
                        "#5C5F66",  # Subtle text
                        "#373A40",  # Border
                        "#2C2E33",  # Background hover
                        "#25262B",  # Background
                        "#1A1B1E",  # Card background
                        "#141517",  # Dark background
                        "#101113"   # Very dark background
                    ]
                },
                "components": {
                    "Button": {
                        "styles": {
                            "root": {
                                "borderRadius": "8px",
                                "fontWeight": 500,
                                "transition": "all 0.2s ease",
                            },
                        },
                    },
                    "Card": {
                        "styles": {
                            "root": {
                                "borderRadius": "12px",
                                "boxShadow": "0 2px 8px rgba(0, 0, 0, 0.2)",
                                "transition": "all 0.3s ease",
                                "&:hover": {
                                    "boxShadow": "0 4px 12px rgba(0, 0, 0, 0.3)",
                                    "transform": "translateY(-2px)",
                                },
                            },
                        },
                    },
                    "Modal": {
                        "styles": {
                            "root": {
                                "borderRadius": "16px",
                            },
                            "header": {
                                "fontWeight": 600,
                            },
                        },
                    },
                },
            }
        else:
            theme = {
                "colorScheme": "light",
                "primaryColor": "blue",
                "colors": {
                    "primary": ["#F0F9FF", "#E0F2FE", "#BAE6FD", "#7DD3FC", "#38BDF8", "#0EA5E9", "#0284C7", "#0369A1", "#075985", "#0C4A6E"],
                    "blue": ["#F0F9FF", "#E0F2FE", "#BAE6FD", "#7DD3FC", "#38BDF8", "#0EA5E9", "#0284C7", "#0369A1", "#075985", "#0C4A6E"],
                    "green": ["#F0FDF4", "#DCFCE7", "#BBF7D0", "#86EFAC", "#4ADE80", "#22C55E", "#16A34A", "#15803D", "#166534", "#14532D"],
                    "red": ["#FEF2F2", "#FEE2E2", "#FECACA", "#FCA5A5", "#F87171", "#EF4444", "#DC2626", "#B91C1C", "#991B1B", "#7F1D1D"],
                    "orange": ["#FFF7ED", "#FFEDD5", "#FED7AA", "#FDBA74", "#FB923C", "#F97316", "#EA580C", "#C2410C", "#9A3412", "#7C2D12"],
                },
                "components": {
                    "Button": {
                        "styles": {
                            "root": {
                                "borderRadius": "8px",
                                "fontWeight": 500,
                                "transition": "all 0.2s ease",
                            },
                        },
                    },
                    "Card": {
                        "styles": {
                            "root": {
                                "borderRadius": "12px",
                                "boxShadow": "0 2px 8px rgba(0, 0, 0, 0.08)",
                                "transition": "all 0.3s ease",
                                "&:hover": {
                                    "boxShadow": "0 4px 12px rgba(0, 0, 0, 0.12)",
                                    "transform": "translateY(-2px)",
                                },
                            },
                        },
                    },
                    "Modal": {
                        "styles": {
                            "root": {
                                "borderRadius": "16px",
                            },
                            "header": {
                                "fontWeight": 600,
                            },
                        },
                    },
                },
            }

        return new_scheme, icon_class, theme

    # Return current scheme and appropriate theme if not triggered by button
    if current_scheme == "dark":
        theme = {
            "colorScheme": "dark",
            "primaryColor": "blue",
            "colors": {
                "dark": [
                    "#C1C2C5",  # Text color
                    "#A6A7AB",  # Secondary text
                    "#909296",  # Tertiary text
                    "#5C5F66",  # Subtle text
                    "#373A40",  # Border
                    "#2C2E33",  # Background hover
                    "#25262B",  # Background
                    "#1A1B1E",  # Card background
                    "#141517",  # Dark background
                    "#101113"   # Very dark background
                ]
            },
            "components": {
                "Button": {
                    "styles": {
                        "root": {
                            "borderRadius": "8px",
                            "fontWeight": 500,
                            "transition": "all 0.2s ease",
                        },
                    },
                },
                "Card": {
                    "styles": {
                        "root": {
                            "borderRadius": "12px",
                            "boxShadow": "0 2px 8px rgba(0, 0, 0, 0.2)",
                            "transition": "all 0.3s ease",
                            "&:hover": {
                                "boxShadow": "0 4px 12px rgba(0, 0, 0, 0.3)",
                                "transform": "translateY(-2px)",
                            },
                        },
                    },
                },
                "Modal": {
                    "styles": {
                        "root": {
                            "borderRadius": "16px",
                        },
                        "header": {
                            "fontWeight": 600,
                        },
                    },
                },
            },
        }
    else:
        theme = {
            "colorScheme": "light",
            "primaryColor": "blue",
            "colors": {
                "primary": ["#F0F9FF", "#E0F2FE", "#BAE6FD", "#7DD3FC", "#38BDF8", "#0EA5E9", "#0284C7", "#0369A1", "#075985", "#0C4A6E"],
                "blue": ["#F0F9FF", "#E0F2FE", "#BAE6FD", "#7DD3FC", "#38BDF8", "#0EA5E9", "#0284C7", "#0369A1", "#075985", "#0C4A6E"],
                "green": ["#F0FDF4", "#DCFCE7", "#BBF7D0", "#86EFAC", "#4ADE80", "#22C55E", "#16A34A", "#15803D", "#166534", "#14532D"],
                "red": ["#FEF2F2", "#FEE2E2", "#FECACA", "#FCA5A5", "#F87171", "#EF4444", "#DC2626", "#B91C1C", "#991B1B", "#7F1D1D"],
                "orange": ["#FFF7ED", "#FFEDD5", "#FED7AA", "#FDBA74", "#FB923C", "#F97316", "#EA580C", "#C2410C", "#9A3412", "#7C2D12"],
            },
            "components": {
                "Button": {
                    "styles": {
                        "root": {
                            "borderRadius": "8px",
                            "fontWeight": 500,
                            "transition": "all 0.2s ease",
                        },
                    },
                },
                "Card": {
                    "styles": {
                        "root": {
                            "borderRadius": "12px",
                            "boxShadow": "0 2px 8px rgba(0, 0, 0, 0.08)",
                            "transition": "all 0.3s ease",
                            "&:hover": {
                                "boxShadow": "0 4px 12px rgba(0, 0, 0, 0.12)",
                                "transform": "translateY(-2px)",
                            },
                        },
                    },
                },
                "Modal": {
                    "styles": {
                        "root": {
                            "borderRadius": "16px",
                        },
                        "header": {
                            "fontWeight": 600,
                        },
                    },
                },
            },
        }

    return current_scheme, icon_class, theme
