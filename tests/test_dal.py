# tests/test_dal.py

import pytest
import sqlite3
import os
from datetime import datetime, timedelta

# Adjust import path if necessary, assuming tests are run from project root
from app import dal
from app import database_setup

# --- Test Setup & Teardown --- 

TEST_DB_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')
TEST_DB_PATH = os.path.join(TEST_DB_DIR, 'test_biomarkers.db')

@pytest.fixture(scope='module', autouse=True)
def setup_test_database():
    """Sets up a clean test database before module tests and cleans up after."""
    # Ensure data directory exists
    os.makedirs(TEST_DB_DIR, exist_ok=True)

    # Point DAL and setup to the test database for the duration of the tests
    original_db_path = dal.DATABASE_PATH
    original_setup_path = database_setup.DATABASE_PATH
    dal.DATABASE_PATH = TEST_DB_PATH
    database_setup.DATABASE_PATH = TEST_DB_PATH

    # Initialize the schema in the test DB
    database_setup.initialize_database()

    yield # Run the tests

    # Teardown: Remove the test database file
    dal.DATABASE_PATH = original_db_path # Restore original path
    database_setup.DATABASE_PATH = original_setup_path
    try:
        os.remove(TEST_DB_PATH)
        print(f"\nTest database {TEST_DB_PATH} removed.")
    except OSError as e:
        print(f"Error removing test database: {e}")

@pytest.fixture(autouse=True)
def clear_tables_between_tests():
    """Clears data from tables before each test function."""
    conn = dal.get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            # Delete readings first due to foreign key constraint
            cursor.execute("DELETE FROM Readings")
            cursor.execute("DELETE FROM Biomarkers")
            # Reset autoincrement counters (optional but good practice for testing)
            cursor.execute("DELETE FROM sqlite_sequence WHERE name='Readings'")
            cursor.execute("DELETE FROM sqlite_sequence WHERE name='Biomarkers'")
            conn.commit()
        except sqlite3.Error as e:
            print(f"Error clearing tables: {e}")
        finally:
            conn.close()

# --- Biomarker Tests --- 

def test_add_biomarker_success():
    biomarker_id = dal.add_biomarker("Test Glucose", "mg/dL", "Sugar")
    assert biomarker_id == 1
    biomarker = dal.get_biomarker_by_id(biomarker_id)
    assert biomarker is not None
    assert biomarker['name'] == "Test Glucose"
    assert biomarker['unit'] == "mg/dL"
    assert biomarker['category'] == "Sugar"

def test_add_biomarker_duplicate():
    dal.add_biomarker("Test Cholesterol", "mg/dL")
    biomarker_id_duplicate = dal.add_biomarker("Test Cholesterol", "mmol/L") # Same name
    assert biomarker_id_duplicate is None

def test_get_all_biomarkers():
    dal.add_biomarker("Test A", "unit A", "Cat 1")
    dal.add_biomarker("Test C", "unit C", "Cat 2")
    dal.add_biomarker("Test B", "unit B", "Cat 1")
    biomarkers = dal.get_all_biomarkers()
    assert len(biomarkers) == 3
    # Check order (by category, then name)
    assert biomarkers[0]['name'] == "Test A"
    assert biomarkers[1]['name'] == "Test B"
    assert biomarkers[2]['name'] == "Test C"

def test_get_biomarker_by_id_found():
    biomarker_id = dal.add_biomarker("Specific Test", "units")
    biomarker = dal.get_biomarker_by_id(biomarker_id)
    assert biomarker['id'] == biomarker_id
    assert biomarker['name'] == "Specific Test"

def test_get_biomarker_by_id_not_found():
    biomarker = dal.get_biomarker_by_id(999)
    assert biomarker is None

def test_update_biomarker_success():
    biomarker_id = dal.add_biomarker("Old Name", "old unit")
    updated = dal.update_biomarker(biomarker_id, "New Name", "new unit", "New Cat")
    assert updated is True
    biomarker = dal.get_biomarker_by_id(biomarker_id)
    assert biomarker['name'] == "New Name"
    assert biomarker['unit'] == "new unit"
    assert biomarker['category'] == "New Cat"

def test_update_biomarker_duplicate_name():
    id1 = dal.add_biomarker("Name 1", "unit 1")
    id2 = dal.add_biomarker("Name 2", "unit 2")
    updated = dal.update_biomarker(id2, "Name 1", "unit 2") # Try to rename to existing name
    assert updated is False
    biomarker2 = dal.get_biomarker_by_id(id2)
    assert biomarker2['name'] == "Name 2"

def test_update_biomarker_not_found():
    updated = dal.update_biomarker(999, "Ghost Name", "ghost unit")
    assert updated is False

def test_delete_biomarker_success():
    biomarker_id = dal.add_biomarker("To Delete", "units")
    dal.add_reading(biomarker_id, datetime.now().isoformat(), 10.0) # Add reading to test cascade
    deleted = dal.delete_biomarker(biomarker_id)
    assert deleted is True
    assert dal.get_biomarker_by_id(biomarker_id) is None
    # Check cascade delete worked
    readings = dal.get_readings_for_biomarker(biomarker_id)
    assert len(readings) == 0

def test_delete_biomarker_not_found():
    deleted = dal.delete_biomarker(999)
    assert deleted is False

# --- Reading Tests --- 

def test_add_reading_success():
    biomarker_id = dal.add_biomarker("Reading Test", "units")
    ts = datetime.now().isoformat()
    reading_id = dal.add_reading(biomarker_id, ts, 123.45)
    assert reading_id == 1
    reading = dal.get_reading_by_id(reading_id)
    assert reading is not None
    assert reading['biomarker_id'] == biomarker_id
    assert reading['timestamp'] == ts
    assert reading['value'] == 123.45

def test_add_reading_invalid_biomarker_id():
    ts = datetime.now().isoformat()
    reading_id = dal.add_reading(999, ts, 10.0) # Non-existent biomarker_id
    assert reading_id is None

def test_add_reading_invalid_timestamp():
    biomarker_id = dal.add_biomarker("Timestamp Test", "units")
    reading_id = dal.add_reading(biomarker_id, "not-a-date", 10.0)
    assert reading_id is None

def test_get_readings_for_biomarker():
    b_id = dal.add_biomarker("Multi Reading", "units")
    ts1 = (datetime.now() - timedelta(days=2)).isoformat()
    ts2 = (datetime.now() - timedelta(days=1)).isoformat()
    ts3 = datetime.now().isoformat()
    dal.add_reading(b_id, ts2, 20.0)
    dal.add_reading(b_id, ts1, 10.0)
    dal.add_reading(b_id, ts3, 30.0)

    readings = dal.get_readings_for_biomarker(b_id)
    assert len(readings) == 3
    # Check order (ASC)
    assert readings[0]['timestamp'] == ts1
    assert readings[1]['timestamp'] == ts2
    assert readings[2]['timestamp'] == ts3

def test_get_readings_for_biomarker_with_dates():
    b_id = dal.add_biomarker("Date Filter", "units")
    ts1 = (datetime.now() - timedelta(days=3)).isoformat()
    ts2 = (datetime.now() - timedelta(days=2)).isoformat() # Start date
    ts3 = (datetime.now() - timedelta(days=1)).isoformat()
    ts4 = datetime.now().isoformat() # End date
    ts5 = (datetime.now() + timedelta(days=1)).isoformat()
    dal.add_reading(b_id, ts1, 1.0)
    dal.add_reading(b_id, ts2, 2.0)
    dal.add_reading(b_id, ts3, 3.0)
    dal.add_reading(b_id, ts4, 4.0)
    dal.add_reading(b_id, ts5, 5.0)

    readings = dal.get_readings_for_biomarker(b_id, start_date=ts2, end_date=ts4)
    assert len(readings) == 3
    assert readings[0]['timestamp'] == ts2
    assert readings[1]['timestamp'] == ts3
    assert readings[2]['timestamp'] == ts4

def test_get_readings_for_biomarker_no_readings():
    b_id = dal.add_biomarker("No Readings Yet", "units")
    readings = dal.get_readings_for_biomarker(b_id)
    assert len(readings) == 0

def test_get_reading_by_id_found():
    b_id = dal.add_biomarker("Get Reading", "units")
    ts = datetime.now().isoformat()
    r_id = dal.add_reading(b_id, ts, 55.5)
    reading = dal.get_reading_by_id(r_id)
    assert reading['id'] == r_id
    assert reading['value'] == 55.5

def test_get_reading_by_id_not_found():
    reading = dal.get_reading_by_id(999)
    assert reading is None

def test_update_reading_success():
    b_id = dal.add_biomarker("Update Reading", "units")
    ts_old = datetime.now().isoformat()
    r_id = dal.add_reading(b_id, ts_old, 1.0)
    ts_new = (datetime.now() + timedelta(hours=1)).isoformat()
    updated = dal.update_reading(r_id, ts_new, 2.0)
    assert updated is True
    reading = dal.get_reading_by_id(r_id)
    assert reading['timestamp'] == ts_new
    assert reading['value'] == 2.0

def test_update_reading_invalid_timestamp():
    b_id = dal.add_biomarker("Update Invalid TS", "units")
    ts_old = datetime.now().isoformat()
    r_id = dal.add_reading(b_id, ts_old, 1.0)
    updated = dal.update_reading(r_id, "not-a-valid-date", 2.0)
    assert updated is False
    reading = dal.get_reading_by_id(r_id)
    assert reading['timestamp'] == ts_old # Should not have changed

def test_update_reading_not_found():
    ts = datetime.now().isoformat()
    updated = dal.update_reading(999, ts, 100.0)
    assert updated is False

def test_delete_reading_success():
    b_id = dal.add_biomarker("Delete Reading", "units")
    ts = datetime.now().isoformat()
    r_id = dal.add_reading(b_id, ts, 99.0)
    deleted = dal.delete_reading(r_id)
    assert deleted is True
    assert dal.get_reading_by_id(r_id) is None

def test_delete_reading_not_found():
    deleted = dal.delete_reading(999)
    assert deleted is False 