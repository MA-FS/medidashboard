import sqlite3
import os
from datetime import datetime

# Database path configuration (reuse from database_setup or define centrally)
DATABASE_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')
DATABASE_PATH = os.path.join(DATABASE_DIR, 'biomarkers.db')

def get_db_connection():
    """Establishes a connection to the SQLite database with improved error handling for concurrent access."""
    conn = None
    max_retries = 3
    retry_delay = 0.5  # seconds

    for attempt in range(max_retries):
        try:
            conn = sqlite3.connect(DATABASE_PATH, timeout=10.0)  # Increased timeout for busy database
            conn.row_factory = sqlite3.Row  # Return rows as dictionary-like objects
            conn.execute("PRAGMA foreign_keys = ON;")  # Enforce foreign key constraints
            return conn
        except sqlite3.OperationalError as e:
            # Handle database locked errors (concurrent access)
            if "database is locked" in str(e) and attempt < max_retries - 1:
                print(f"Database locked, retrying in {retry_delay} seconds... (Attempt {attempt + 1}/{max_retries})")
                import time
                time.sleep(retry_delay)
                continue
            print(f"Database operational error after {attempt + 1} attempts: {e}")
            return None
        except sqlite3.Error as e:
            print(f"Database connection error: {e}")
            return None

# --- Biomarker CRUD ---

def add_biomarker(name: str, unit: str, category: str = None):
    """Adds a new biomarker definition to the database."""
    conn = get_db_connection()
    if not conn:
        return None
    try:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO Biomarkers (name, unit, category) VALUES (?, ?, ?)",
            (name, unit, category)
        )
        conn.commit()
        return cursor.lastrowid
    except sqlite3.IntegrityError:
        print(f"Biomarker with name '{name}' already exists.")
        return None
    except sqlite3.Error as e:
        print(f"Error adding biomarker: {e}")
        return None
    finally:
        if conn:
            conn.close()

def get_all_biomarkers():
    """Retrieves all biomarker definitions from the database."""
    conn = get_db_connection()
    if not conn:
        print("DAL: Failed to get database connection in get_all_biomarkers()")
        return []
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, unit, category FROM Biomarkers ORDER BY category, name")
        rows = cursor.fetchall()
        print(f"DAL: Retrieved {len(rows)} biomarker rows from database")

        if not rows:
            print("DAL: No biomarkers found in database")
            return []

        biomarkers = [dict(row) for row in rows]
        return biomarkers
    except sqlite3.Error as e:
        print(f"Error getting biomarkers: {e}")
        import traceback
        traceback.print_exc()
        return []
    finally:
        if conn:
            conn.close()

def get_biomarker_by_id(biomarker_id: int):
    """Retrieves a specific biomarker by its ID."""
    conn = get_db_connection()
    if not conn:
        return None
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, unit, category FROM Biomarkers WHERE id = ?", (biomarker_id,))
        row = cursor.fetchone()
        return dict(row) if row else None
    except sqlite3.Error as e:
        print(f"Error getting biomarker by ID: {e}")
        return None
    finally:
        if conn:
            conn.close()

def update_biomarker(biomarker_id: int, name: str, unit: str, category: str = None):
    """Updates an existing biomarker definition."""
    conn = get_db_connection()
    if not conn:
        return False
    try:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE Biomarkers SET name = ?, unit = ?, category = ? WHERE id = ?",
            (name, unit, category, biomarker_id)
        )
        conn.commit()
        return cursor.rowcount > 0 # Returns True if a row was updated
    except sqlite3.IntegrityError:
        print(f"Error updating biomarker: A biomarker with name '{name}' might already exist.")
        return False
    except sqlite3.Error as e:
        print(f"Error updating biomarker: {e}")
        return False
    finally:
        if conn:
            conn.close()

def delete_biomarker(biomarker_id: int):
    """Deletes a biomarker definition and its associated readings (due to CASCADE)."""
    conn = get_db_connection()
    if not conn:
        return False
    try:
        cursor = conn.cursor()
        # Foreign key constraint with ON DELETE CASCADE handles Readings deletion
        cursor.execute("DELETE FROM Biomarkers WHERE id = ?", (biomarker_id,))
        conn.commit()
        return cursor.rowcount > 0 # Returns True if a row was deleted
    except sqlite3.Error as e:
        print(f"Error deleting biomarker: {e}")
        return False
    finally:
        if conn:
            conn.close()

# --- Reading CRUD ---

def add_reading(biomarker_id: int, timestamp: str, value: float):
    """Adds a new biomarker reading."""
    conn = get_db_connection()
    if not conn:
        return None
    try:
        # Validate timestamp format (basic check)
        datetime.fromisoformat(timestamp)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO Readings (biomarker_id, timestamp, value) VALUES (?, ?, ?)",
            (biomarker_id, timestamp, value)
        )
        conn.commit()
        return cursor.lastrowid
    except ValueError:
         print(f"Invalid timestamp format: {timestamp}. Use ISO 8601 format.")
         return None
    except sqlite3.IntegrityError:
        print(f"Error adding reading: Biomarker ID {biomarker_id} likely does not exist.")
        return None
    except sqlite3.Error as e:
        print(f"Error adding reading: {e}")
        return None
    finally:
        if conn:
            conn.close()

def get_readings_for_biomarker(biomarker_id: int, start_date: str = None, end_date: str = None):
    """Retrieves readings for a specific biomarker, optionally filtered by date range."""
    conn = get_db_connection()
    if not conn:
        return []
    try:
        cursor = conn.cursor()
        query = "SELECT id, biomarker_id, timestamp, value FROM Readings WHERE biomarker_id = ?"
        params = [biomarker_id]

        if start_date:
            query += " AND timestamp >= ?"
            params.append(start_date)
        if end_date:
            query += " AND timestamp <= ?"
            params.append(end_date)

        query += " ORDER BY timestamp ASC"

        cursor.execute(query, params)
        readings = [dict(row) for row in cursor.fetchall()]
        return readings
    except sqlite3.Error as e:
        print(f"Error getting readings: {e}")
        return []
    finally:
        if conn:
            conn.close()

def get_all_readings_with_biomarker_details():
    """Retrieves all readings with biomarker details (name, unit, category)."""
    conn = get_db_connection()
    if not conn:
        return []
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT
                r.id as reading_id,
                r.biomarker_id,
                r.timestamp,
                r.value,
                b.name as biomarker_name,
                b.unit,
                b.category
            FROM Readings r
            JOIN Biomarkers b ON r.biomarker_id = b.id
            ORDER BY b.name, r.timestamp
        """)
        readings = [dict(row) for row in cursor.fetchall()]
        return readings
    except sqlite3.Error as e:
        print(f"Error getting readings with biomarker details: {e}")
        return []
    finally:
        if conn:
            conn.close()

def get_reading_by_id(reading_id: int):
    """Retrieves a specific reading by its ID."""
    conn = get_db_connection()
    if not conn:
        return None
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT id, biomarker_id, timestamp, value FROM Readings WHERE id = ?", (reading_id,))
        row = cursor.fetchone()
        return dict(row) if row else None
    except sqlite3.Error as e:
        print(f"Error getting reading by ID: {e}")
        return None
    finally:
        if conn:
            conn.close()

def check_reading_exists(biomarker_id: int, timestamp: str):
    """Checks if a reading with the same biomarker_id and timestamp already exists."""
    conn = get_db_connection()
    if not conn:
        return False
    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id FROM Readings WHERE biomarker_id = ? AND timestamp = ?",
            (biomarker_id, timestamp)
        )
        row = cursor.fetchone()
        return row is not None
    except sqlite3.Error as e:
        print(f"Error checking if reading exists: {e}")
        return False
    finally:
        if conn:
            conn.close()

def update_reading(reading_id: int, timestamp: str, value: float):
    """Updates an existing reading."""
    conn = get_db_connection()
    if not conn:
        return False
    try:
        # Validate timestamp format (basic check)
        datetime.fromisoformat(timestamp)
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE Readings SET timestamp = ?, value = ? WHERE id = ?",
            (timestamp, value, reading_id)
        )
        conn.commit()
        return cursor.rowcount > 0
    except ValueError:
         print(f"Invalid timestamp format: {timestamp}. Use ISO 8601 format.")
         return False
    except sqlite3.Error as e:
        print(f"Error updating reading: {e}")
        return False
    finally:
        if conn:
            conn.close()

def delete_reading(reading_id: int):
    """Deletes a specific reading."""
    conn = get_db_connection()
    if not conn:
        return False
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM Readings WHERE id = ?", (reading_id,))
        conn.commit()
        return cursor.rowcount > 0
    except sqlite3.Error as e:
        print(f"Error deleting reading: {e}")
        return False
    finally:
        if conn:
            conn.close()

# --- Reference Range CRUD ---

def add_reference_range(biomarker_id: int, range_type: str, lower_bound: float = None, upper_bound: float = None):
    """Adds a new reference range for a biomarker."""
    conn = get_db_connection()
    if not conn:
        return None
    try:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO ReferenceRanges (biomarker_id, range_type, lower_bound, upper_bound) VALUES (?, ?, ?, ?)",
            (biomarker_id, range_type, lower_bound, upper_bound)
        )
        conn.commit()
        return cursor.lastrowid
    except sqlite3.IntegrityError:
        print(f"Error adding reference range: Biomarker ID {biomarker_id} likely does not exist.")
        return None
    except sqlite3.Error as e:
        print(f"Error adding reference range: {e}")
        return None
    finally:
        if conn:
            conn.close()

def get_reference_range(biomarker_id: int):
    """Gets the reference range for a biomarker."""
    conn = get_db_connection()
    if not conn:
        return None
    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, biomarker_id, range_type, lower_bound, upper_bound FROM ReferenceRanges WHERE biomarker_id = ?",
            (biomarker_id,)
        )
        row = cursor.fetchone()
        if row:
            return dict(row)
        return None
    except sqlite3.Error as e:
        print(f"Error getting reference range: {e}")
        return None
    finally:
        if conn:
            conn.close()

def get_all_reference_ranges():
    """Gets all reference ranges."""
    conn = get_db_connection()
    if not conn:
        return []
    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, biomarker_id, range_type, lower_bound, upper_bound FROM ReferenceRanges"
        )
        ranges = [dict(row) for row in cursor.fetchall()]
        return ranges
    except sqlite3.Error as e:
        print(f"Error getting all reference ranges: {e}")
        return []
    finally:
        if conn:
            conn.close()

def update_reference_range(range_id: int, range_type: str, lower_bound: float = None, upper_bound: float = None):
    """Updates a reference range."""
    conn = get_db_connection()
    if not conn:
        return False
    try:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE ReferenceRanges SET range_type = ?, lower_bound = ?, upper_bound = ? WHERE id = ?",
            (range_type, lower_bound, upper_bound, range_id)
        )
        conn.commit()
        return cursor.rowcount > 0
    except sqlite3.Error as e:
        print(f"Error updating reference range: {e}")
        return False
    finally:
        if conn:
            conn.close()

def update_reference_range_by_biomarker_id(biomarker_id: int, range_type: str, lower_bound: float = None, upper_bound: float = None):
    """Updates a reference range by biomarker ID, or creates it if it doesn't exist."""
    conn = get_db_connection()
    if not conn:
        return False
    try:
        cursor = conn.cursor()
        # Check if reference range exists
        cursor.execute("SELECT id FROM ReferenceRanges WHERE biomarker_id = ?", (biomarker_id,))
        row = cursor.fetchone()

        if row:
            # Update existing reference range
            range_id = row['id']
            cursor.execute(
                "UPDATE ReferenceRanges SET range_type = ?, lower_bound = ?, upper_bound = ? WHERE id = ?",
                (range_type, lower_bound, upper_bound, range_id)
            )
        else:
            # Create new reference range
            cursor.execute(
                "INSERT INTO ReferenceRanges (biomarker_id, range_type, lower_bound, upper_bound) VALUES (?, ?, ?, ?)",
                (biomarker_id, range_type, lower_bound, upper_bound)
            )

        conn.commit()
        return True
    except sqlite3.Error as e:
        print(f"Error updating reference range by biomarker ID: {e}")
        return False
    finally:
        if conn:
            conn.close()

def delete_reference_range(range_id: int):
    """Deletes a reference range."""
    conn = get_db_connection()
    if not conn:
        return False
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM ReferenceRanges WHERE id = ?", (range_id,))
        conn.commit()
        return cursor.rowcount > 0
    except sqlite3.Error as e:
        print(f"Error deleting reference range: {e}")
        return False
    finally:
        if conn:
            conn.close()

# --- Backup & Restore ---

def backup_database(backup_file_path: str):
    """Creates a backup of the current database file to the specified path with improved error handling."""
    conn = None
    backup_conn = None
    try:
        # Ensure the source database exists before trying to back it up
        if not os.path.exists(DATABASE_PATH):
            print(f"Error: Source database not found at {DATABASE_PATH}")
            return False, "Source database not found"

        # Check if backup directory exists and is writable
        backup_dir = os.path.dirname(backup_file_path)
        if not os.path.exists(backup_dir):
            try:
                os.makedirs(backup_dir, exist_ok=True)
                print(f"Created backup directory: {backup_dir}")
            except (OSError, PermissionError) as e:
                print(f"Error creating backup directory: {e}")
                return False, f"Cannot create backup directory: {str(e)}"

        # Check if we have write permission to the backup location
        if not os.access(backup_dir, os.W_OK):
            print(f"Error: No write permission to backup directory: {backup_dir}")
            return False, "No write permission to backup directory"

        # Check if there's enough disk space (rough estimate - 2x the DB size plus 10MB buffer)
        try:
            db_size = os.path.getsize(DATABASE_PATH)
            import shutil
            free_space = shutil.disk_usage(backup_dir).free
            if free_space < (db_size * 2) + (10 * 1024 * 1024):  # 2x DB size + 10MB
                print(f"Warning: Low disk space for backup. DB size: {db_size}, Free space: {free_space}")
                # Continue anyway but log the warning
        except OSError as e:
            print(f"Warning: Could not check disk space: {e}")
            # Continue anyway

        # Connect to the source database
        conn = sqlite3.connect(DATABASE_PATH)

        # Create/connect to the backup database file
        backup_conn = sqlite3.connect(backup_file_path)

        # Perform the backup
        with backup_conn:
            conn.backup(backup_conn)

        print(f"Database successfully backed up to {backup_file_path}")
        return True, "Backup successful"
    except sqlite3.Error as e:
        error_msg = f"SQLite error during backup: {e}"
        print(error_msg)
        return False, error_msg
    except (OSError, IOError) as e:
        error_msg = f"File system error during backup: {e}"
        print(error_msg)
        # Clean up potentially incomplete backup file on error
        if os.path.exists(backup_file_path):
            try:
                os.remove(backup_file_path)
                print(f"Removed incomplete backup file: {backup_file_path}")
            except OSError as rm_e:
                print(f"Error removing incomplete backup file {backup_file_path}: {rm_e}")
        return False, error_msg
    finally:
        if conn:
            conn.close()
        if backup_conn:
            backup_conn.close()

def restore_database(uploaded_backup_path: str):
    """Replaces the current database with the uploaded backup file with improved error handling.
    Returns (success, message) tuple where success is True/False and message is a descriptive string.
    Note: This function ONLY replaces the file. Merging logic is handled in BLL.
    """
    try:
        # Validate the uploaded file exists
        if not os.path.exists(uploaded_backup_path):
            print(f"Error: Uploaded backup file not found at {uploaded_backup_path}")
            return False, "Uploaded backup file not found"

        # Validate the uploaded file is a valid SQLite database
        try:
            test_conn = sqlite3.connect(uploaded_backup_path)
            cursor = test_conn.cursor()
            # Check if it has the expected tables
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name IN ('Biomarkers', 'Readings')")
            tables = cursor.fetchall()
            test_conn.close()

            if len(tables) < 2:
                print(f"Error: Uploaded file is not a valid MediDashboard backup (missing tables)")
                return False, "Invalid backup file format (missing required tables)"
        except sqlite3.Error as e:
            print(f"Error: Uploaded file is not a valid SQLite database: {e}")
            return False, f"Invalid backup file format: {str(e)}"

        # Check if we have write permission to the database directory
        db_dir = os.path.dirname(DATABASE_PATH)
        if not os.access(db_dir, os.W_OK):
            print(f"Error: No write permission to database directory: {db_dir}")
            return False, "No write permission to database directory"

        # Create a backup of the current database before replacing it
        import shutil
        from datetime import datetime

        # Generate a timestamped backup filename
        current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
        auto_backup_path = os.path.join(db_dir, f"auto_backup_{current_time}.db")

        try:
            if os.path.exists(DATABASE_PATH):
                shutil.copy2(DATABASE_PATH, auto_backup_path)
                print(f"Created automatic backup of current database at {auto_backup_path}")
        except (OSError, IOError) as e:
            print(f"Warning: Could not create automatic backup before restore: {e}")
            # Continue anyway, but log the warning

        # Now perform the actual restore by copying the uploaded file to the database location
        try:
            # Copy the uploaded backup to the database location
            shutil.copy2(uploaded_backup_path, DATABASE_PATH)
            print(f"Successfully restored database from {uploaded_backup_path}")
            return True, "Database restored successfully"
        except (OSError, IOError) as e:
            error_msg = f"Error during restore: {e}"
            print(error_msg)
            # Try to restore from auto-backup if available
            if os.path.exists(auto_backup_path):
                try:
                    shutil.copy2(auto_backup_path, DATABASE_PATH)
                    print(f"Restored original database from automatic backup after failed restore")
                    return False, f"{error_msg}. Original database restored from backup."
                except (OSError, IOError) as e2:
                    print(f"Error restoring from automatic backup: {e2}")
            return False, error_msg

    except Exception as e:
        print(f"Unexpected error during database restore: {e}")
        return False, f"Unexpected error: {str(e)}"