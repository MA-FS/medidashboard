"""
bll.py - Business Logic Layer for the MediDashboard application.

This module contains the business logic for the application, including:
- Biomarker management (add, update, delete)
- Reading management (record, update, delete)
- Data validation and transformation
- Backup and restore functionality

The BLL sits between the Data Access Layer (DAL) and the UI layer,
providing validation, error handling, and business rules.
"""

from app import dal
from app import validation
from datetime import datetime
import os
import io
import pandas as pd
import base64

# --- Biomarker Management ---

def add_new_biomarker(name: str, unit: str, category: str = None):
    """
    Adds a new biomarker after comprehensive validation.

    This function validates the biomarker name, unit, and category before
    adding it to the database. It performs the following validations:
    - Name must not be empty and must be between 2-50 characters
    - Unit must not be empty and must be less than 20 characters
    - Category (optional) must be less than 30 characters

    Args:
        name (str): The biomarker name (e.g., "Blood Glucose")
        unit (str): The unit of measurement (e.g., "mg/dL")
        category (str, optional): The category for grouping (e.g., "Blood", "Lipids")

    Returns:
        tuple: (result, error_message)
            - If successful: (biomarker_id, "")
            - If failed: (None, error_message)
    """
    # Validate name
    name_valid, name_error = validation.validate_biomarker_name(name)
    if not name_valid:
        print(f"Error: {name_error}")
        return None, name_error

    # Validate unit
    unit_valid, unit_error = validation.validate_biomarker_unit(unit)
    if not unit_valid:
        print(f"Error: {unit_error}")
        return None, unit_error

    # Validate category (if provided)
    if category is not None:
        category_valid, category_error = validation.validate_biomarker_category(category)
        if not category_valid:
            print(f"Error: {category_error}")
            return None, category_error

    # All validations passed, add the biomarker
    cleaned_name = name.strip()
    cleaned_unit = unit.strip()
    cleaned_category = category.strip() if category else None

    result = dal.add_biomarker(cleaned_name, cleaned_unit, cleaned_category)
    if result is None:
        error_msg = f"Failed to add biomarker '{cleaned_name}'. It might already exist or there was a database error."
        return None, error_msg

    return result, ""

def get_all_biomarkers_grouped():
    """Retrieves all biomarkers, potentially grouped by category (future enhancement)."""
    # For now, just return the flat list from DAL
    # Grouping logic can be added here later if needed for UI
    biomarkers = dal.get_all_biomarkers()
    print(f"BLL: Retrieved {len(biomarkers)} biomarkers from DAL")
    if not biomarkers:
        print("WARNING: No biomarkers returned from DAL.get_all_biomarkers()")
    return biomarkers

def get_biomarker_details(biomarker_id: int):
    """Gets details for a single biomarker."""
    return dal.get_biomarker_by_id(biomarker_id)

def update_existing_biomarker(biomarker_id: int, name: str, unit: str, category: str = None):
    """Updates an existing biomarker after comprehensive validation."""
    # Validate name
    name_valid, name_error = validation.validate_biomarker_name(name)
    if not name_valid:
        print(f"Error: {name_error}")
        return False, name_error

    # Validate unit
    unit_valid, unit_error = validation.validate_biomarker_unit(unit)
    if not unit_valid:
        print(f"Error: {unit_error}")
        return False, unit_error

    # Validate category (if provided)
    if category is not None:
        category_valid, category_error = validation.validate_biomarker_category(category)
        if not category_valid:
            print(f"Error: {category_error}")
            return False, category_error

    # All validations passed, update the biomarker
    cleaned_name = name.strip()
    cleaned_unit = unit.strip()
    cleaned_category = category.strip() if category else None

    result = dal.update_biomarker(biomarker_id, cleaned_name, cleaned_unit, cleaned_category)
    if not result:
        error_msg = f"Failed to update biomarker ID {biomarker_id}. The name '{cleaned_name}' might already exist or there was a database error."
        return False, error_msg

    return True, ""

def remove_biomarker(biomarker_id: int):
    """Removes a biomarker."""
    return dal.delete_biomarker(biomarker_id)

# --- Reading Management ---

def record_new_reading(biomarker_id: int, timestamp_str: str, value_str: str):
    """
    Records a new biomarker reading after comprehensive validation and type conversion.

    This function validates the biomarker ID, reading value, and timestamp before
    adding the reading to the database. It performs the following validations:
    - Biomarker ID must exist in the database
    - Reading value must be a valid number within a reasonable range
    - Timestamp must be in a recognized format and not in the future

    Args:
        biomarker_id (int): The ID of the biomarker for this reading
        timestamp_str (str): The timestamp of the reading in a recognized format
        value_str (str): The reading value as a string (will be converted to float)

    Returns:
        tuple: (result, error_message)
            - If successful: (reading_id, "")
            - If failed: (None, error_message)
    """
    # Validate biomarker ID
    biomarker_valid, biomarker_error = validation.validate_biomarker_id(biomarker_id)
    if not biomarker_valid:
        print(f"Error: {biomarker_error}")
        return None, biomarker_error

    # Validate reading value
    value_valid, value_error, value = validation.validate_reading_value(value_str)
    if not value_valid:
        print(f"Error: {value_error}")
        return None, value_error

    # Validate timestamp
    timestamp_valid, timestamp_error, formatted_timestamp = validation.validate_reading_timestamp(timestamp_str)
    if not timestamp_valid:
        print(f"Error: {timestamp_error}")
        return None, timestamp_error

    # All validations passed, add the reading
    result = dal.add_reading(biomarker_id, formatted_timestamp, value)
    if result is None:
        error_msg = f"Failed to save reading. Database error or biomarker ID {biomarker_id} does not exist."
        return None, error_msg

    return result, ""

def get_readings_for_display(biomarker_id: int, start_date: str = None, end_date: str = None):
    """
    Retrieves readings for a specific biomarker, suitable for display (e.g., plotting).

    This function fetches readings for a given biomarker, optionally filtered by date range.

    Args:
        biomarker_id (int): The ID of the biomarker to fetch readings for
        start_date (str, optional): The start date for filtering readings (ISO format)
        end_date (str, optional): The end date for filtering readings (ISO format)

    Returns:
        list: A list of reading dictionaries, each containing 'id', 'biomarker_id',
              'timestamp', and 'value' keys
    """
    # Validate biomarker_id to avoid errors
    if biomarker_id is None or not isinstance(biomarker_id, int) or biomarker_id <= 0:
        print(f"Warning: Invalid biomarker_id: {biomarker_id}")
        return []
    # Potentially add data transformation logic here if needed before display
    readings = dal.get_readings_for_biomarker(biomarker_id, start_date, end_date)
    # Example transformation: Convert timestamp strings to datetime objects if needed by Plotly
    # for reading in readings:
    #     reading['timestamp'] = datetime.fromisoformat(reading['timestamp'])
    return readings

def get_reading_details(reading_id: int):
    """Gets details for a single reading."""
    return dal.get_reading_by_id(reading_id)

def update_existing_reading(reading_id: int, timestamp_str: str, value_str: str):
    """Updates an existing reading after comprehensive validation."""
    # Validate reading value
    value_valid, value_error, value = validation.validate_reading_value(value_str)
    if not value_valid:
        print(f"Error: {value_error}")
        return False, value_error

    # Validate timestamp
    timestamp_valid, timestamp_error, formatted_timestamp = validation.validate_reading_timestamp(timestamp_str)
    if not timestamp_valid:
        print(f"Error: {timestamp_error}")
        return False, timestamp_error

    # All validations passed, update the reading
    result = dal.update_reading(reading_id, formatted_timestamp, value)
    if not result:
        error_msg = f"Failed to update reading ID {reading_id}. The reading might not exist or there was a database error."
        return False, error_msg

    return True, ""

def remove_reading(reading_id: int):
    """Removes a reading."""
    return dal.delete_reading(reading_id)

def delete_biomarker_reading(reading_id: int):
    """
    Deletes a biomarker reading.

    Args:
        reading_id (int): The ID of the reading to delete

    Returns:
        tuple: (success, error_message)
            - success (bool): True if deletion was successful, False otherwise
            - error_message (str): Error message if deletion failed, empty string otherwise
    """
    try:
        # Validate reading_id
        if not reading_id or not isinstance(reading_id, int) or reading_id <= 0:
            return False, "Invalid reading ID"

        # Get the reading to make sure it exists
        reading = dal.get_reading_by_id(reading_id)
        if not reading:
            return False, f"Reading with ID {reading_id} not found"

        # Delete the reading
        success = dal.delete_reading(reading_id)
        if success:
            return True, ""
        else:
            return False, "Failed to delete reading"
    except Exception as e:
        print(f"Error deleting reading: {str(e)}")
        return False, f"Error deleting reading: {str(e)}"

# --- Reference Range Management ---

def add_reference_range(biomarker_id: int, range_type: str, lower_bound=None, upper_bound=None):
    """
    Adds a reference range for a biomarker with validation.

    Args:
        biomarker_id (int): The ID of the biomarker
        range_type (str): The type of range ('below', 'above', 'between')
        lower_bound (float, optional): The lower bound of the range
        upper_bound (float, optional): The upper bound of the range

    Returns:
        tuple: (result, error_message)
            - If successful: (range_id, "")
            - If failed: (None, error_message)
    """
    # Validate biomarker_id
    if not biomarker_id or not isinstance(biomarker_id, int) or biomarker_id <= 0:
        return None, "Invalid biomarker ID"

    # Validate range_type
    valid_range_types = ['below', 'above', 'between']
    if range_type not in valid_range_types:
        return None, f"Invalid range type. Must be one of: {', '.join(valid_range_types)}"

    # Validate bounds based on range_type
    if range_type == 'below' and upper_bound is None:
        return None, "Upper bound is required for 'below' range type"

    if range_type == 'above' and lower_bound is None:
        return None, "Lower bound is required for 'above' range type"

    if range_type == 'between':
        if lower_bound is None or upper_bound is None:
            return None, "Both lower and upper bounds are required for 'between' range type"
        if lower_bound >= upper_bound:
            return None, "Lower bound must be less than upper bound"

    # Check if reference range already exists for this biomarker
    existing_range = dal.get_reference_range(biomarker_id)
    if existing_range:
        # Update existing range instead of adding a new one
        result = dal.update_reference_range(existing_range['id'], range_type, lower_bound, upper_bound)
        if not result:
            return None, "Failed to update reference range"
        return existing_range['id'], ""

    # Add new reference range
    result = dal.add_reference_range(biomarker_id, range_type, lower_bound, upper_bound)
    if result is None:
        return None, "Failed to add reference range"

    return result, ""

def get_reference_range_for_biomarker(biomarker_id: int):
    """Gets the reference range for a biomarker."""
    return dal.get_reference_range(biomarker_id)

def get_all_reference_ranges():
    """Gets all reference ranges."""
    return dal.get_all_reference_ranges()

def is_value_in_range(value, reference_range):
    """
    Determines if a value is within a reference range.

    Args:
        value (float): The value to check
        reference_range (dict): The reference range to check against

    Returns:
        bool or None: True if in range, False if out of range, None if no range defined
    """
    if not reference_range:
        return None  # No reference range defined

    range_type = reference_range['range_type']
    lower_bound = reference_range['lower_bound']
    upper_bound = reference_range['upper_bound']

    if range_type == 'below':
        return value < upper_bound
    elif range_type == 'above':
        return value > lower_bound
    elif range_type == 'between':
        return lower_bound <= value <= upper_bound

    return None  # Invalid range type

def update_reference_range(range_id: int, range_type: str, lower_bound=None, upper_bound=None):
    """
    Updates a reference range with validation.

    Args:
        range_id (int): The ID of the reference range
        range_type (str): The type of range ('below', 'above', 'between')
        lower_bound (float, optional): The lower bound of the range
        upper_bound (float, optional): The upper bound of the range

    Returns:
        tuple: (success, error_message)
            - If successful: (True, "")
            - If failed: (False, error_message)
    """
    # Validate range_type
    valid_range_types = ['below', 'above', 'between']
    if range_type not in valid_range_types:
        return False, f"Invalid range type. Must be one of: {', '.join(valid_range_types)}"

    # Validate bounds based on range_type
    if range_type == 'below' and upper_bound is None:
        return False, "Upper bound is required for 'below' range type"

    if range_type == 'above' and lower_bound is None:
        return False, "Lower bound is required for 'above' range type"

    if range_type == 'between':
        if lower_bound is None or upper_bound is None:
            return False, "Both lower and upper bounds are required for 'between' range type"
        if lower_bound >= upper_bound:
            return False, "Lower bound must be less than upper bound"

    # Update reference range
    result = dal.update_reference_range(range_id, range_type, lower_bound, upper_bound)
    if not result:
        return False, "Failed to update reference range"

    return True, ""

def update_reference_range_by_biomarker(biomarker_id: int, range_type: str, lower_bound=None, upper_bound=None):
    """
    Updates a reference range by biomarker ID, or creates it if it doesn't exist.

    Args:
        biomarker_id (int): The ID of the biomarker
        range_type (str): The type of range ('below', 'above', 'between')
        lower_bound (float, optional): The lower bound of the range
        upper_bound (float, optional): The upper bound of the range

    Returns:
        tuple: (success, error_message)
            - If successful: (True, "")
            - If failed: (False, error_message)
    """
    # Validate biomarker_id
    if not biomarker_id or not isinstance(biomarker_id, int) or biomarker_id <= 0:
        return False, "Invalid biomarker ID"

    # Validate range_type
    valid_range_types = ['below', 'above', 'between']
    if range_type not in valid_range_types:
        return False, f"Invalid range type. Must be one of: {', '.join(valid_range_types)}"

    # Validate bounds based on range_type
    if range_type == 'below' and upper_bound is None:
        return False, "Upper bound is required for 'below' range type"

    if range_type == 'above' and lower_bound is None:
        return False, "Lower bound is required for 'above' range type"

    if range_type == 'between':
        if lower_bound is None or upper_bound is None:
            return False, "Both lower and upper bounds are required for 'between' range type"
        if lower_bound >= upper_bound:
            return False, "Lower bound must be less than upper bound"

    # Update or create reference range
    result = dal.update_reference_range_by_biomarker_id(biomarker_id, range_type, lower_bound, upper_bound)
    if not result:
        return False, "Failed to update reference range"

    return True, ""

def remove_reference_range(range_id: int):
    """Removes a reference range."""
    return dal.delete_reference_range(range_id)

# --- CSV Handling Functions ---

def decode_csv_content(base64_content):
    """
    Decodes base64 encoded CSV content with multiple encoding attempts.

    Args:
        base64_content (str): Base64 encoded content string

    Returns:
        str: Decoded CSV content

    Raises:
        ValueError: If content cannot be decoded with any supported encoding
    """
    # Extract the content part from the data URL
    if ',' in base64_content:
        _, content_string = base64_content.split(',')
    else:
        content_string = base64_content

    # Decode base64
    binary_content = base64.b64decode(content_string)

    # Try different encodings
    encodings = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1', 'utf-16']

    for encoding in encodings:
        try:
            decoded = binary_content.decode(encoding)
            print(f"Successfully decoded CSV with {encoding} encoding")
            return decoded
        except UnicodeDecodeError:
            continue

    # If we get here, none of the encodings worked
    raise ValueError(
        "Could not decode the CSV file with any supported encoding. "
        "Please ensure your file is saved with UTF-8 encoding or try "
        "resaving it in a different format."
    )

# --- Backup & Restore Logic ---

def create_backup_file():
    """
    Creates a backup file of the database and returns its path.

    This function creates a timestamped backup of the current database file.
    The backup is stored in the same directory as the original database.

    Returns:
        str or None: The path to the backup file if successful, None if failed
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_filename = f"medidashboard_backup_{timestamp}.db"
    # Place backup temporarily in the same data dir (consider a dedicated temp dir later)
    backup_filepath = os.path.join(dal.DATABASE_DIR, backup_filename)

    print(f"Attempting backup to: {backup_filepath}")
    success_result = dal.backup_database(backup_filepath)

    # Handle the tuple return value from backup_database
    if isinstance(success_result, tuple) and len(success_result) >= 1:
        success = success_result[0]
    else:
        success = success_result

    if success:
        return backup_filepath
    else:
        return None

def perform_restore_from_file(uploaded_backup_path: str):
    """
    Handles the full restore process including intelligent biomarker merging.

    This function restores the database from a backup file and performs
    intelligent merging of biomarker definitions. The process includes:
    1. Fetching current biomarker definitions before overwrite
    2. Replacing the database file with the backup
    3. Fetching biomarker definitions from the restored database
    4. Re-adding any biomarker definitions that were in the original database
       but not in the backup (preserving user-created biomarkers)

    Args:
        uploaded_backup_path (str): Path to the uploaded backup file

    Returns:
        dict: A dictionary with the following keys:
            - success (bool): Whether the restore was successful
            - message (str): A message describing the result
            - added_biomarkers (int): Number of biomarkers re-added from the original database
    """
    print(f"Starting restore process from: {uploaded_backup_path}")
    added_count = 0

    # --- Step 1: Get current biomarker definitions (before overwrite) ---
    print("Fetching current biomarker definitions...")
    current_biomarkers = dal.get_all_biomarkers()
    current_biomarker_set = set((b['name'], b['unit']) for b in current_biomarkers)
    print(f"Found {len(current_biomarker_set)} unique current biomarkers.")

    # --- Step 2: Replace database file ---
    print("Replacing database file...")
    restore_success = dal.restore_database(uploaded_backup_path)

    if not restore_success:
        return {'success': False, 'message': "Error replacing database file.", 'added_biomarkers': 0}

    # --- Step 3: Database replaced. Now connect to the *new* DB to get backup biomarkers ---
    print("Fetching biomarker definitions from restored database...")
    # Need to ensure connections are fresh to the *new* file
    # DAL functions handle connection opening/closing per call
    restored_biomarkers = dal.get_all_biomarkers()
    restored_biomarker_set = set((b['name'], b['unit']) for b in restored_biomarkers)
    print(f"Found {len(restored_biomarker_set)} unique biomarkers in restored DB.")

    # --- Step 4: Intelligent Biomarker Merging ---
    print("Performing intelligent biomarker merge...")
    for biomarker in restored_biomarkers:
        key = (biomarker['name'], biomarker['unit'])
        if key not in current_biomarker_set:
            # This definition was in the backup but not the original DB.
            # We need to re-add it to the *new* database if it doesn't already exist
            # (it *shouldn't* exist based on restore_success replacing the file,
            # but double-check to be safe and handle edge cases).

            # Check if it *now* exists in the restored DB (it should)
            # This logic seems slightly off based on PRD. PRD says:
            # "Any biomarker definitions present in the backup file but not currently defined
            # in the application (based on an exact match of Name and Unit) will be added
            # to the application's list of defined biomarkers."
            # This implies we compare backup biomarkers to *original* biomarkers.
            # If a biomarker (Name, Unit) was in backup but NOT original, it should be added.
            # But since the entire DB was replaced, all biomarkers from backup *are* the current ones.
            # The PRD might be interpreted as: preserve definitions created since the backup.

            # Let's reinterpret: Ensure all biomarkers from the *original* database that
            # are *not* present in the restored database are re-added.
            pass # Initial interpretation was complex, let's stick to PRD intent.

    # PRD Reinterpretation for Merge:
    # 1. Database file is fully replaced by the backup. Readings are now backup readings.
    # 2. Compare biomarker definitions (name, unit) from the *original* DB (`current_biomarker_set`)
    #    with definitions now in the *restored* DB (`restored_biomarker_set`).
    # 3. Any definition present in the *original* set but NOT in the *restored* set needs to be added back.

    added_count = 0
    biomarkers_to_re_add = [] # Definitions from original DB missing in the backup DB

    for biomarker in current_biomarkers: # Iterate through original definitions
         key = (biomarker['name'], biomarker['unit'])
         if key not in restored_biomarker_set:
             biomarkers_to_re_add.append(biomarker)

    if biomarkers_to_re_add:
        print(f"Found {len(biomarkers_to_re_add)} biomarkers from original DB missing in backup. Re-adding...")
        for biomarker in biomarkers_to_re_add:
            print(f"  Re-adding: {biomarker['name']} ({biomarker['unit']}) - Category: {biomarker.get('category')}")
            # Use the DAL add function on the *now current* (restored) database
            add_result = dal.add_biomarker(biomarker['name'], biomarker['unit'], biomarker.get('category'))
            if add_result is not None:
                added_count += 1
            else:
                 print(f"  Warning: Failed to re-add biomarker {biomarker['name']}")
                 # Decide if this should cause overall failure?
                 # For now, continue but report potential issues.
    else:
         print("No missing original biomarkers found in the restored database.")

    message = f"Restore successful. Database replaced. {added_count} biomarker definitions preserved from before restore."
    print(message)
    return {'success': True, 'message': message, 'added_biomarkers': added_count}

def validate_csv_content(csv_content, show_all_rows=False):
    """
    Validates CSV content without importing.

    This function parses a CSV file containing biomarker readings and validates each row
    without adding any data to the database. It checks for:
    - Required columns
    - Biomarker existence
    - Date and time format
    - Value format

    Args:
        csv_content (str): The content of the CSV file as a string
        show_all_rows (bool): If True, include all rows in the preview regardless of file size

    Returns:
        dict: Validation results including row-by-row analysis
    """
    # Initialize result
    validation_results = {
        'is_valid': True,
        'total_rows': 0,
        'valid_rows': 0,
        'invalid_rows': 0,
        'row_results': [],
        'column_issues': [],
        'general_issues': [],
        'preview_data': []
    }

    try:
        # Parse CSV with comment handling
        df = pd.read_csv(io.StringIO(csv_content), comment='#', skip_blank_lines=True)
        validation_results['total_rows'] = len(df)

        # Check required columns
        required_columns = ['Biomarker Name', 'Date', 'Value']
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            validation_results['is_valid'] = False
            validation_results['column_issues'].append(f"Missing required columns: {', '.join(missing_columns)}")
            return validation_results

        # Get all biomarkers for validation
        all_biomarkers = dal.get_all_biomarkers()
        biomarker_map = {}
        for b in all_biomarkers:
            # Map by name (lowercase)
            biomarker_map[b['name'].lower()] = b['id']
            # Map by name+unit (lowercase)
            if b['unit']:
                biomarker_map[f"{b['name'].lower()}|{b['unit'].lower()}"] = b['id']

        # Determine how many rows to show in preview
        # If show_all_rows is True, include all rows regardless of file size
        if show_all_rows or len(df) <= 50:  # For small files or when explicitly requested, show all rows
            preview_df = df.copy()
            preview_df['Row Number'] = [idx + 2 for idx in range(len(df))]  # +2 for header and 0-indexing
            validation_results['preview_data'] = preview_df.to_dict('records')
        else:
            # For larger files, we need to be selective
            # First, validate all rows to identify which ones have errors
            invalid_row_indices = []

            # Temporary validation to find invalid rows (we'll do full validation later)
            for index, row in df.iterrows():
                try:
                    # Basic validation to identify problematic rows
                    biomarker_name = str(row['Biomarker Name']).strip() if not pd.isna(row['Biomarker Name']) else ""
                    date_str = str(row['Date']).strip() if not pd.isna(row['Date']) else ""
                    value_str = str(row['Value']).strip() if not pd.isna(row['Value']) else ""

                    # Check biomarker existence
                    biomarker_id = None
                    unit_str = str(row.get('Unit', '')).strip() if 'Unit' in row and not pd.isna(row['Unit']) else ''

                    # Try to match by name+unit first
                    if unit_str:
                        key = f"{biomarker_name.lower()}|{unit_str.lower()}"
                        if key in biomarker_map:
                            biomarker_id = biomarker_map[key]

                    # If no match by name+unit, try just by name
                    if biomarker_id is None:
                        if biomarker_name.lower() in biomarker_map:
                            biomarker_id = biomarker_map[biomarker_name.lower()]

                    # Check if any basic validation fails
                    if (not biomarker_name or biomarker_id is None or
                        not date_str or not value_str):
                        invalid_row_indices.append(index)
                    else:
                        # Check date format
                        try:
                            datetime.strptime(date_str, "%Y-%m-%d")
                        except ValueError:
                            invalid_row_indices.append(index)
                            continue

                        # Check value format
                        try:
                            float(value_str)
                        except ValueError:
                            invalid_row_indices.append(index)
                            continue

                        # Check time format if provided
                        time_str = str(row.get('Time', '')).strip() if 'Time' in row and not pd.isna(row['Time']) else ''
                        if time_str:
                            try:
                                datetime.strptime(time_str, "%H:%M")
                            except ValueError:
                                invalid_row_indices.append(index)
                                continue
                except Exception:
                    invalid_row_indices.append(index)

            # If there are invalid rows, include them all plus some context
            if invalid_row_indices:
                # Create a set of rows to include in the preview
                rows_to_include = set()

                # Include all invalid rows
                for idx in invalid_row_indices:
                    rows_to_include.add(idx)

                    # Add more context rows before and after each invalid row (increased from 2 to 5)
                    for context_idx in range(max(0, idx-5), min(len(df), idx+6)):
                        rows_to_include.add(context_idx)

                # Also include the first few and last few rows for context
                for idx in range(min(10, len(df))):
                    rows_to_include.add(idx)

                for idx in range(max(0, len(df)-10), len(df)):
                    rows_to_include.add(idx)

                # Convert to sorted list
                rows_list = sorted(list(rows_to_include))

                # Create a new DataFrame with just these rows
                preview_df = df.iloc[rows_list].copy()

                # Add a note about row numbers to help users understand
                preview_df['Row Number'] = [idx + 2 for idx in rows_list]  # +2 for header and 0-indexing

                # Convert to dict for the preview
                validation_results['preview_data'] = preview_df.to_dict('records')

                # Add a flag to indicate that we're showing a subset of rows
                validation_results['showing_subset'] = True
                validation_results['has_errors'] = True
            else:
                # No invalid rows found, show first and last rows
                first_rows = min(25, len(df) // 2)
                last_rows = min(25, len(df) - first_rows)

                if first_rows + last_rows >= len(df):
                    # If we're showing most of the file anyway, just show all
                    preview_df = df.copy()
                    preview_df['Row Number'] = [idx + 2 for idx in range(len(df))]  # +2 for header and 0-indexing
                    validation_results['showing_subset'] = False
                else:
                    # Combine first and last rows
                    preview_df = pd.concat([df.head(first_rows), df.tail(last_rows)])

                    # Add row numbers
                    row_indices = list(preview_df.index)
                    preview_df['Row Number'] = [idx + 2 for idx in row_indices]  # +2 for header and 0-indexing

                    # Add a flag to indicate that we're showing a subset of rows
                    validation_results['showing_subset'] = True
                    validation_results['has_errors'] = False

                validation_results['preview_data'] = preview_df.to_dict('records')

        # Validate each row
        for index, row in df.iterrows():
            row_result = {
                'row_number': index + 2,  # +2 for header and 0-indexing
                'is_valid': True,
                'issues': []
            }

            # Extract and validate data
            try:
                biomarker_name = str(row['Biomarker Name']).strip() if not pd.isna(row['Biomarker Name']) else ""
                date_str = str(row['Date']).strip() if not pd.isna(row['Date']) else ""
                value_str = str(row['Value']).strip() if not pd.isna(row['Value']) else ""

                # Check biomarker name
                if not biomarker_name:
                    row_result['is_valid'] = False
                    row_result['issues'].append("Biomarker Name is required")
                else:
                    # Try to match biomarker
                    biomarker_id = None
                    unit_str = str(row.get('Unit', '')).strip() if 'Unit' in row and not pd.isna(row['Unit']) else ''

                    # Try to match by name+unit first
                    if unit_str:
                        key = f"{biomarker_name.lower()}|{unit_str.lower()}"
                        if key in biomarker_map:
                            biomarker_id = biomarker_map[key]

                    # If no match by name+unit, try just by name
                    if biomarker_id is None:
                        if biomarker_name.lower() in biomarker_map:
                            biomarker_id = biomarker_map[biomarker_name.lower()]

                    if biomarker_id is None:
                        row_result['is_valid'] = False
                        row_result['issues'].append(f"Biomarker '{biomarker_name}' not found")

                # Validate date
                if not date_str:
                    row_result['is_valid'] = False
                    row_result['issues'].append("Date is required")
                else:
                    try:
                        datetime.strptime(date_str, "%Y-%m-%d")
                    except ValueError:
                        row_result['is_valid'] = False
                        row_result['issues'].append(f"Invalid date format: '{date_str}'. Use YYYY-MM-DD")

                # Validate value
                if not value_str:
                    row_result['is_valid'] = False
                    row_result['issues'].append("Value is required")
                else:
                    try:
                        float(value_str)
                    except ValueError:
                        row_result['is_valid'] = False
                        row_result['issues'].append(f"Invalid value: '{value_str}'. Must be a number")

                # Validate time if provided
                time_str = str(row.get('Time', '')).strip() if 'Time' in row and not pd.isna(row['Time']) else ''
                if time_str:
                    try:
                        datetime.strptime(time_str, "%H:%M")
                    except ValueError:
                        row_result['is_valid'] = False
                        row_result['issues'].append(f"Invalid time format: '{time_str}'. Use HH:MM")

            except Exception as e:
                row_result['is_valid'] = False
                row_result['issues'].append(f"Error processing row: {str(e)}")

            # Add row result to results
            validation_results['row_results'].append(row_result)
            if row_result['is_valid']:
                validation_results['valid_rows'] += 1
            else:
                validation_results['invalid_rows'] += 1
                validation_results['is_valid'] = False

        return validation_results

    except Exception as e:
        validation_results['is_valid'] = False
        validation_results['general_issues'].append(f"Error parsing CSV file: {str(e)}")
        return validation_results

def export_readings_to_csv():
    """
    Exports all biomarker readings to CSV format.

    Returns:
        str: CSV content as a string
    """
    # Get all readings with biomarker details
    readings = dal.get_all_readings_with_biomarker_details()

    if not readings:
        return "Biomarker Name,Date,Time,Value,Unit\n# No readings found"

    # Create CSV content
    csv_content = "Biomarker Name,Date,Time,Value,Unit\n"

    for reading in readings:
        # Split timestamp into date and time and ensure correct format
        timestamp = reading['timestamp']

        try:
            # Parse the timestamp to ensure consistent formatting
            if ' ' in timestamp:
                dt = datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")
            else:
                dt = datetime.strptime(timestamp, "%Y-%m-%d")

            # Format date as YYYY-MM-DD and time as HH:MM
            date_part = dt.strftime("%Y-%m-%d")
            time_part = dt.strftime("%H:%M")
        except ValueError:
            # Fallback if parsing fails
            date_part = timestamp.split(' ')[0] if ' ' in timestamp else timestamp
            time_part = timestamp.split(' ')[1].rsplit(':', 1)[0] if ' ' in timestamp and len(timestamp.split(' ')) > 1 else "00:00"

        # Format the row
        row = f"{reading['biomarker_name']},{date_part},{time_part},{reading['value']},{reading['unit']}\n"
        csv_content += row

    return csv_content

def import_readings_from_csv(csv_content, skip_duplicates=True):
    """
    Imports biomarker readings from a CSV file.

    This function parses a CSV file containing biomarker readings and adds them to the database.
    The CSV file should have the following columns:
    - Biomarker Name (required): Must match an existing biomarker name
    - Date (required): In YYYY-MM-DD format
    - Time (optional): In HH:MM format
    - Value (required): The reading value
    - Unit (optional): Helps match with existing biomarkers

    Args:
        csv_content (str): The content of the CSV file as a string
        skip_duplicates (bool): Whether to skip duplicate readings (default: True)

    Returns:
        dict: A dictionary with the following keys:
            - success (bool): Whether the import was successful
            - message (str): A message describing the result
            - total_rows (int): Total number of rows in the CSV
            - imported_count (int): Number of readings successfully imported
            - error_count (int): Number of readings that failed to import
            - skipped_count (int): Number of duplicate readings that were skipped
            - errors (list): List of error messages for failed imports
    """
    # First validate the CSV content
    validation_results = validate_csv_content(csv_content)

    if not validation_results['is_valid']:
        return {
            'success': False,
            'message': "CSV validation failed. Please fix the issues and try again.",
            'total_rows': validation_results['total_rows'],
            'imported_count': 0,
            'error_count': validation_results['invalid_rows'],
            'skipped_count': 0,
            'errors': [issue for row in validation_results['row_results'] if not row['is_valid'] for issue in [f"Row {row['row_number']}: {', '.join(row['issues'])}"]]
        }

    # Initialize result counters
    total_rows = validation_results['total_rows']
    imported_count = 0
    error_count = 0
    skipped_count = 0
    errors = []

    try:
        # Parse the CSV content with comment handling
        df = pd.read_csv(io.StringIO(csv_content), comment='#', skip_blank_lines=True)

        # Get all biomarkers for matching
        all_biomarkers = dal.get_all_biomarkers()
        biomarker_map = {}
        for b in all_biomarkers:
            # Map by name (lowercase)
            biomarker_map[b['name'].lower()] = b['id']
            # Map by name+unit (lowercase)
            if b['unit']:
                biomarker_map[f"{b['name'].lower()}|{b['unit'].lower()}"] = b['id']

        # Process each row
        for index, row in df.iterrows():
            try:
                # Extract data from row
                biomarker_name = str(row['Biomarker Name']).strip() if not pd.isna(row['Biomarker Name']) else ""
                date_str = str(row['Date']).strip() if not pd.isna(row['Date']) else ""
                value_str = str(row['Value']).strip() if not pd.isna(row['Value']) else ""

                # Handle optional columns
                time_str = str(row.get('Time', '00:00')).strip() if 'Time' in row and not pd.isna(row['Time']) else '00:00'
                unit_str = str(row.get('Unit', '')).strip() if 'Unit' in row and not pd.isna(row['Unit']) else ''

                # Match biomarker
                biomarker_id = None

                # Try to match by name+unit first (more precise)
                if unit_str:
                    key = f"{biomarker_name.lower()}|{unit_str.lower()}"
                    if key in biomarker_map:
                        biomarker_id = biomarker_map[key]

                # If no match by name+unit, try just by name
                if biomarker_id is None:
                    if biomarker_name.lower() in biomarker_map:
                        biomarker_id = biomarker_map[biomarker_name.lower()]

                if biomarker_id is None:
                    error_msg = f"Row {index+2}: Biomarker '{biomarker_name}' not found"
                    errors.append(error_msg)
                    error_count += 1
                    continue

                # Combine date and time
                timestamp_str = f"{date_str} {time_str}:00"

                # Validate and format the timestamp
                timestamp_valid, timestamp_error, formatted_timestamp = validation.validate_reading_timestamp(timestamp_str)
                if not timestamp_valid:
                    error_msg = f"Row {index+2}: {timestamp_error}"
                    errors.append(error_msg)
                    error_count += 1
                    continue

                # Check if reading already exists
                if skip_duplicates and dal.check_reading_exists(biomarker_id, formatted_timestamp):
                    print(f"Skipping duplicate reading for biomarker {biomarker_name} at {formatted_timestamp}")
                    skipped_count += 1
                    continue

                # Add the reading
                result, error = record_new_reading(biomarker_id, formatted_timestamp, value_str)
                if result is None:
                    error_msg = f"Row {index+2}: {error}"
                    errors.append(error_msg)
                    error_count += 1
                else:
                    imported_count += 1

            except Exception as e:
                error_msg = f"Row {index+2}: {str(e)}"
                errors.append(error_msg)
                error_count += 1

        # Generate result message
        if imported_count == total_rows:
            message = f"Successfully imported all {imported_count} readings."
            success = True
        elif imported_count > 0:
            message = f"Partially successful: Imported {imported_count} out of {total_rows} readings."
            if error_count > 0:
                message += f" {error_count} errors."
            if skipped_count > 0:
                message += f" {skipped_count} duplicates skipped."
            success = True
        else:
            message = f"Import failed: No readings were imported."
            if error_count > 0:
                message += f" {error_count} errors."
            if skipped_count > 0:
                message += f" {skipped_count} duplicates skipped."
            success = False

        return {
            'success': success,
            'message': message,
            'total_rows': total_rows,
            'imported_count': imported_count,
            'error_count': error_count,
            'skipped_count': skipped_count,
            'errors': errors
        }

    except Exception as e:
        return {
            'success': False,
            'message': f"Error parsing CSV file: {str(e)}",
            'total_rows': 0,
            'imported_count': 0,
            'error_count': 0,
            'skipped_count': 0,
            'errors': [f"Error parsing CSV file: {str(e)}"]
        }