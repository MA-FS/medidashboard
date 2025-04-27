"""
validation.py - Contains validation functions for user inputs.
This module provides comprehensive validation for biomarker and reading inputs.
"""

from datetime import datetime
import re

# --- Biomarker Validation ---

def validate_biomarker_name(name):
    """
    Validates a biomarker name.
    
    Args:
        name (str): The biomarker name to validate
        
    Returns:
        tuple: (is_valid, error_message)
    """
    if not name or not name.strip():
        return False, "Biomarker name cannot be empty."
    
    if len(name.strip()) < 2:
        return False, "Biomarker name must be at least 2 characters long."
    
    if len(name.strip()) > 50:
        return False, "Biomarker name cannot exceed 50 characters."
    
    # Check for invalid characters (optional)
    if re.search(r'[^\w\s\-\(\)]', name.strip()):
        return False, "Biomarker name contains invalid characters. Use only letters, numbers, spaces, hyphens, and parentheses."
    
    return True, ""

def validate_biomarker_unit(unit):
    """
    Validates a biomarker unit.
    
    Args:
        unit (str): The biomarker unit to validate
        
    Returns:
        tuple: (is_valid, error_message)
    """
    if not unit or not unit.strip():
        return False, "Biomarker unit cannot be empty."
    
    if len(unit.strip()) > 20:
        return False, "Biomarker unit cannot exceed 20 characters."
    
    return True, ""

def validate_biomarker_category(category):
    """
    Validates a biomarker category.
    
    Args:
        category (str): The biomarker category to validate
        
    Returns:
        tuple: (is_valid, error_message)
    """
    # Category can be None or empty
    if category is None or not category.strip():
        return True, ""
    
    if len(category.strip()) > 30:
        return False, "Biomarker category cannot exceed 30 characters."
    
    return True, ""

# --- Reading Validation ---

def validate_reading_value(value_str):
    """
    Validates a reading value.
    
    Args:
        value_str (str): The reading value to validate
        
    Returns:
        tuple: (is_valid, error_message, converted_value)
    """
    if not value_str or not value_str.strip():
        return False, "Reading value cannot be empty.", None
    
    try:
        value = float(value_str)
        
        # Check for reasonable range (optional, depends on biomarker)
        if value < -1000000 or value > 1000000:
            return False, "Reading value is outside reasonable range.", None
        
        return True, "", value
    except ValueError:
        return False, "Reading value must be a number.", None

def validate_reading_timestamp(timestamp_str):
    """
    Validates a reading timestamp.
    
    Args:
        timestamp_str (str): The timestamp to validate
        
    Returns:
        tuple: (is_valid, error_message, formatted_timestamp)
    """
    if not timestamp_str or not timestamp_str.strip():
        return False, "Timestamp cannot be empty.", None
    
    # Try different formats
    formats = [
        "%Y-%m-%d %H:%M:%S",  # ISO format with space
        "%Y-%m-%dT%H:%M:%S",  # ISO format with T
        "%Y-%m-%d",           # Date only
        "%d/%m/%Y %H:%M:%S",  # UK format
        "%m/%d/%Y %H:%M:%S",  # US format
        "%d-%m-%Y %H:%M:%S",  # Alternative format
        "%m-%d-%Y %H:%M:%S",  # Alternative format
    ]
    
    for fmt in formats:
        try:
            dt = datetime.strptime(timestamp_str.strip(), fmt)
            
            # If date-only format, set time to midnight
            if fmt == "%Y-%m-%d" or fmt == "%d/%m/%Y" or fmt == "%m/%d/%Y" or fmt == "%d-%m-%Y" or fmt == "%m-%d-%Y":
                dt = dt.replace(hour=0, minute=0, second=0)
            
            # Check if date is in the future
            if dt > datetime.now():
                return False, "Timestamp cannot be in the future.", None
            
            # Format in ISO format for storage
            formatted_timestamp = dt.strftime("%Y-%m-%d %H:%M:%S")
            return True, "", formatted_timestamp
        except ValueError:
            continue
    
    return False, "Invalid timestamp format. Use YYYY-MM-DD HH:MM:SS or similar format.", None

def validate_biomarker_id(biomarker_id):
    """
    Validates a biomarker ID.
    
    Args:
        biomarker_id: The biomarker ID to validate
        
    Returns:
        tuple: (is_valid, error_message)
    """
    if biomarker_id is None:
        return False, "Biomarker must be selected."
    
    try:
        biomarker_id = int(biomarker_id)
        if biomarker_id <= 0:
            return False, "Invalid biomarker ID."
        return True, ""
    except (ValueError, TypeError):
        return False, "Invalid biomarker ID."
