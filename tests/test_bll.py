# tests/test_bll.py

import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta

# Adjust import path
from app import bll
from app import dal # We will mock functions from this module

# --- Biomarker Tests --- 

@patch('app.bll.dal.add_biomarker')
def test_add_new_biomarker_success(mock_dal_add):
    mock_dal_add.return_value = 1 # Simulate successful add, return new ID
    result = bll.add_new_biomarker("  Test Glucose ", " mg/dL  ", " Sugar ")
    assert result == 1
    mock_dal_add.assert_called_once_with("Test Glucose", "mg/dL", "Sugar") # Check stripping

@patch('app.bll.dal.add_biomarker')
def test_add_new_biomarker_empty_name(mock_dal_add):
    result = bll.add_new_biomarker("", "mg/dL")
    assert result is None
    mock_dal_add.assert_not_called()

@patch('app.bll.dal.add_biomarker')
def test_add_new_biomarker_empty_unit(mock_dal_add):
    result = bll.add_new_biomarker("Glucose", "")
    assert result is None
    mock_dal_add.assert_not_called()

@patch('app.bll.dal.get_all_biomarkers')
def test_get_all_biomarkers_grouped(mock_dal_get_all):
    mock_data = [
        {'id': 1, 'name': 'A', 'unit': 'uA', 'category': 'C1'},
        {'id': 2, 'name': 'B', 'unit': 'uB', 'category': 'C1'}
    ]
    mock_dal_get_all.return_value = mock_data
    result = bll.get_all_biomarkers_grouped()
    assert result == mock_data
    mock_dal_get_all.assert_called_once()
    # Add tests for grouping logic here if implemented later

@patch('app.bll.dal.get_biomarker_by_id')
def test_get_biomarker_details(mock_dal_get_by_id):
    mock_data = {'id': 1, 'name': 'A', 'unit': 'uA', 'category': 'C1'}
    mock_dal_get_by_id.return_value = mock_data
    result = bll.get_biomarker_details(1)
    assert result == mock_data
    mock_dal_get_by_id.assert_called_once_with(1)

@patch('app.bll.dal.update_biomarker')
def test_update_existing_biomarker_success(mock_dal_update):
    mock_dal_update.return_value = True
    result = bll.update_existing_biomarker(1, " New Name ", " new/unit ", " CatNew ")
    assert result is True
    mock_dal_update.assert_called_once_with(1, "New Name", "new/unit", "CatNew") # Check stripping

@patch('app.bll.dal.update_biomarker')
def test_update_existing_biomarker_empty_name(mock_dal_update):
    result = bll.update_existing_biomarker(1, " ", "unit")
    assert result is False
    mock_dal_update.assert_not_called()

@patch('app.bll.dal.delete_biomarker')
def test_remove_biomarker(mock_dal_delete):
    mock_dal_delete.return_value = True
    result = bll.remove_biomarker(5)
    assert result is True
    mock_dal_delete.assert_called_once_with(5)

# --- Reading Tests --- 

@patch('app.bll.dal.add_reading')
def test_record_new_reading_success(mock_dal_add_reading):
    mock_dal_add_reading.return_value = 10 # Simulate successful add
    ts = datetime.now().isoformat()
    result = bll.record_new_reading(1, ts, " 123.45 ")
    assert result == 10
    mock_dal_add_reading.assert_called_once_with(1, ts, 123.45) # Check value conversion

@patch('app.bll.dal.add_reading')
def test_record_new_reading_invalid_value(mock_dal_add_reading):
    ts = datetime.now().isoformat()
    result = bll.record_new_reading(1, ts, "abc")
    assert result is None
    mock_dal_add_reading.assert_not_called()

@patch('app.bll.dal.add_reading')
def test_record_new_reading_invalid_timestamp(mock_dal_add_reading):
    result = bll.record_new_reading(1, "not-a-date", "123.45")
    assert result is None
    mock_dal_add_reading.assert_not_called()

@patch('app.bll.dal.add_reading')
def test_record_new_reading_none_biomarker_id(mock_dal_add_reading):
    ts = datetime.now().isoformat()
    result = bll.record_new_reading(None, ts, "123.45")
    assert result is None
    mock_dal_add_reading.assert_not_called()

@patch('app.bll.dal.get_readings_for_biomarker')
def test_get_readings_for_display(mock_dal_get_readings):
    ts1 = (datetime.now() - timedelta(days=1)).isoformat()
    ts2 = datetime.now().isoformat()
    mock_data = [
        {'id': 1, 'biomarker_id': 5, 'timestamp': ts1, 'value': 10.0},
        {'id': 2, 'biomarker_id': 5, 'timestamp': ts2, 'value': 12.0}
    ]
    mock_dal_get_readings.return_value = mock_data
    result = bll.get_readings_for_display(5, start_date="2023-01-01", end_date="2023-12-31")
    assert result == mock_data # No transformation currently in BLL
    mock_dal_get_readings.assert_called_once_with(5, "2023-01-01", "2023-12-31")
    # Add tests for data transformation here if implemented later

@patch('app.bll.dal.get_readings_for_biomarker')
def test_get_readings_for_display_none_biomarker(mock_dal_get_readings):
     result = bll.get_readings_for_display(None)
     assert result == []
     mock_dal_get_readings.assert_not_called()

@patch('app.bll.dal.get_reading_by_id')
def test_get_reading_details(mock_dal_get_reading):
    mock_data = {'id': 1, 'biomarker_id': 5, 'timestamp': datetime.now().isoformat(), 'value': 10.0}
    mock_dal_get_reading.return_value = mock_data
    result = bll.get_reading_details(1)
    assert result == mock_data
    mock_dal_get_reading.assert_called_once_with(1)

@patch('app.bll.dal.update_reading')
def test_update_existing_reading_success(mock_dal_update_reading):
    mock_dal_update_reading.return_value = True
    ts = datetime.now().isoformat()
    result = bll.update_existing_reading(5, ts, " 99.9 ")
    assert result is True
    mock_dal_update_reading.assert_called_once_with(5, ts, 99.9) # Check value conversion

@patch('app.bll.dal.update_reading')
def test_update_existing_reading_invalid_value(mock_dal_update_reading):
    ts = datetime.now().isoformat()
    result = bll.update_existing_reading(5, ts, "xyz")
    assert result is False
    mock_dal_update_reading.assert_not_called()

@patch('app.bll.dal.update_reading')
def test_update_existing_reading_invalid_timestamp(mock_dal_update_reading):
    result = bll.update_existing_reading(5, "invalid-date", "99.9")
    assert result is False
    mock_dal_update_reading.assert_not_called()

@patch('app.bll.dal.delete_reading')
def test_remove_reading(mock_dal_delete_reading):
    mock_dal_delete_reading.return_value = True
    result = bll.remove_reading(15)
    assert result is True
    mock_dal_delete_reading.assert_called_once_with(15) 