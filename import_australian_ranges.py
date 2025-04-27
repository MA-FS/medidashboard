#!/usr/bin/env python3
"""
import_australian_ranges.py - Script to import Australian reference ranges for biomarkers.

This script adds reference ranges for biomarkers based on the Australian recommended ranges.
"""

import sys
import os

# Add the parent directory to the Python path so we can import the app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import bll, dal

def import_australian_ranges():
    """
    Imports Australian reference ranges for biomarkers.
    
    This function:
    1. Defines reference ranges for biomarkers based on Australian standards
    2. Adds or updates the reference ranges in the database
    3. Prints a summary of the operations performed
    """
    print("Importing Australian reference ranges for biomarkers...")
    
    # Define reference ranges
    # Format: (biomarker_name, range_type, lower_bound, upper_bound)
    # range_type can be 'below', 'above', or 'between'
    reference_ranges = [
        # Lipid Profile
        ("HDL Cholesterol", "above", 0.9, None),
        ("LDL Cholesterol", "below", None, 3.1),
        ("Non-HDL Cholesterol", "below", None, 4.1),
        ("Triglycerides", "below", None, 2.1),
        ("VLDL", "between", 0.16, 0.67),
        ("Total LDL", "between", 1.53, 3.32),
        ("Total IDL", "between", 0.52, 1.73),
        ("Total Small Dense LDL", "between", 0, 0.15),
        ("Small Dense LDL 3", "between", 0, 0.15),
        
        # Blood Sugar Levels
        ("Glucose (Fasting)", "between", 3, 5.4),
        ("DCCT HbA1c", "below", None, 6.5),
        
        # Kidney Function
        ("Creatinine", "between", 60, 110),
        ("eGFR", "above", 59, None),
        ("BUN (Blood Urea Nitrogen)", "between", 3.5, 8),
        ("Uric Acid", "between", 0.21, 0.43),
        
        # Liver Function
        ("AST (SGOT)", "between", 5, 35),
        ("ALT (SGPT)", "between", 5, 40),
        ("Globulin", "between", 23, 39),
        ("ALP (Alkaline Phosphatase)", "between", 30, 110),
        ("Bilirubin (Total)", "between", 3, 20),
        ("Gamma GT", "between", 5, 50),
        ("Total Protein", "between", 60, 80),
        ("Albumin", "between", 35, 50),
        
        # Electrolytes
        ("Sodium", "between", 135, 145),
        ("Potassium", "between", 3.5, 5.2),
        ("Chloride", "between", 95, 110),
        ("Calcium", "between", 2.1, 2.6),
        ("Adjusted Calcium", "between", 2.1, 2.6),
        ("Phosphate", "between", 0.7, 1.5),
        ("Magnesium", "between", 0.7, 1.1),
        ("Bicarbonate", "between", 22, 32),
        ("Anion Gap", "between", 9, 19),
        
        # Complete Blood Count
        ("White Blood Cell (WBC) Count", "between", 4, 11),
        ("Red Blood Cell (RBC) Count", "between", 4.5, 6.5),
        ("Haemoglobin", "between", 125, 175),
        ("Hematocrit (HCT)", "between", 0.4, 0.55),
        ("Platelet Count", "between", 150, 450),
        ("Mean Corpuscular Volume (MCV)", "between", 80, 99),
        ("Mean Corpuscular Hemoglobin (MCH)", "between", 27, 34),
        ("Mean Corpuscular Hemoglobin Concentration (MCHC)", "between", 310, 360),
        ("Red Cell Distribution Width (RDW)", "between", 11, 15),
        ("Neutrophils", "between", 2, 8),
        ("Lymphocytes", "between", 1, 4),
        ("Monocytes", "below", None, 1.1),
        ("Eosinophils", "below", None, 0.7),
        ("Basophils", "below", None, 0.3),
        ("MPV", "between", 7.1, 11.2),
        
        # Thyroid Function
        ("TSH (Thyroid Stimulating Hormone)", "between", 0.4, 4),
        ("Free T4", "between", 9, 20),
        ("Free T3", "between", 3.5, 6.5),
        
        # Inflammation Markers
        ("hsCRP", "below", None, 1),
        ("Homocysteine (Fasting)", "below", None, 10),
        
        # Vitamins and Minerals
        ("Vitamin D", "above", 50, None),
        ("Vitamin B12", "above", 180, None),
        ("Folate", "above", 10, None),
        ("Ferritin", "between", 30, 500),
        ("Iron", "between", 10, 30),
        ("Transferrin", "between", 2.1, 3.8),
        ("Transferrin Saturation", "between", 15, 50),
        
        # Hormones
        ("Luteinizing Hormone", "below", None, 6),
        ("Follicle Stimulating Hormone", "between", 2, 18),
        ("Testosterone", "between", 8, 27.8),
        ("Estradiol", "below", None, 150),
        ("Prolactin", "between", 45, 375),
        ("DHEA-Sulphate", "between", 2.2, 15.2),
        ("Free Testosterone", "between", 200, 600),
        ("SHBG (Sex Hormone Binding Globulin)", "between", 15, 50),
        ("Insulin-Like Growth Factor", "between", 8.2, 29),
        ("Insulin (Fasting)", "between", 2, 12),
    ]
    
    # Get all biomarkers
    all_biomarkers = dal.get_all_biomarkers()
    biomarker_map = {b['name'].lower(): b['id'] for b in all_biomarkers}
    
    # Add or update reference ranges
    added_count = 0
    updated_count = 0
    skipped_count = 0
    
    for name, range_type, lower_bound, upper_bound in reference_ranges:
        # Try to find the biomarker by name
        biomarker_id = biomarker_map.get(name.lower())
        
        if biomarker_id is None:
            print(f"Skipping {name}: Biomarker not found in database")
            skipped_count += 1
            continue
        
        # Check if reference range already exists
        existing_range = dal.get_reference_range(biomarker_id)
        
        if existing_range:
            # Update existing range
            result = dal.update_reference_range(existing_range['id'], range_type, lower_bound, upper_bound)
            if result:
                print(f"Updated reference range for {name}")
                updated_count += 1
            else:
                print(f"Failed to update reference range for {name}")
                skipped_count += 1
        else:
            # Add new range
            result = dal.add_reference_range(biomarker_id, range_type, lower_bound, upper_bound)
            if result:
                print(f"Added reference range for {name}")
                added_count += 1
            else:
                print(f"Failed to add reference range for {name}")
                skipped_count += 1
    
    print(f"Import complete: Added {added_count}, Updated {updated_count}, Skipped {skipped_count} reference ranges")

if __name__ == '__main__':
    # Run the import function
    import_australian_ranges()
