#!/usr/bin/env python3
"""
update_biomarker_units.py - Script to update biomarker units in the MediDashboard database.

This script updates the units for all biomarkers in the database to match the specified units.
"""

import sys
import os

# Add the parent directory to the Python path so we can import the app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import dal

def update_biomarker_units():
    """
    Updates the units for all biomarkers in the database to match the specified units.
    """
    print("Updating biomarker units...")
    
    # Define the biomarker units dictionary
    biomarker_units = {
        # Lipid Profile
        "Total Cholesterol": "mmol/L",
        "HDL Cholesterol": "mmol/L",
        "LDL Cholesterol": "mmol/L",
        "Non-HDL Cholesterol": "mmol/L",
        "Triglycerides": "mmol/L",
        "LDL/HDL Ratio": "ratio",
        "Chol/HDL Ratio": "ratio",
        "Triglyceride / HDL Ratio": "ratio",
        "VLDL": "mmol/L",
        "Total LDL": "mmol/L",
        "Total IDL": "mmol/L",
        "Total Small Dense LDL": "mmol/L",
        "Small Dense LDL 3": "mg/dL",
        "Small Dense LDL 4": "mg/dL",
        "Small Dense LDL 5": "mg/dL",
        "Small Dense LDL 6": "mg/dL",
        "Small Dense LDL 7": "mg/dL",
        "Mean Size": "nm",
        "Apolipoprotein B": "g/L",
        "Lipoprotein (a)": "g/L",
        
        # Blood Sugar Levels
        "Glucose (Fasting)": "mmol/L",
        "DCCT HbA1c": "%",
        "IFCC HbA1c": "mmol/mol",
        "Estimated Avg Glucose": "mmol/L",
        
        # Kidney Function
        "Creatinine": "µmol/L",
        "eGFR": "mL/min/1.73m2",
        "BUN (Blood Urea Nitrogen)": "mmol/L",
        "Uric Acid": "mmol/L",
        
        # Liver Function
        "AST (SGOT)": "U/L",
        "ALT (SGPT)": "U/L",
        "Globulin": "g/L",
        "ALP (Alkaline Phosphatase)": "U/L",
        "Bilirubin (Total)": "µmol/L",
        "Bilirubin (Direct)": "µmol/L",
        "Bilirubin (Indirect)": "µmol/L",
        "Gamma GT": "U/L",
        "Total Protein": "g/L",
        "Albumin": "g/L",
        
        # Electrolytes
        "Sodium": "mmol/L",
        "Potassium": "mmol/L",
        "Chloride": "mmol/L",
        "Calcium": "mmol/L",
        "Adjusted Calcium": "mmol/L",
        "Phosphate": "mmol/L",
        "Magnesium": "mmol/L",
        "Bicarbonate": "mmol/L",
        "Anion Gap": "mmol/L",
        
        # Complete Blood Count (CBC)
        "White Blood Cell (WBC) Count": "x10^9/L",
        "Red Blood Cell (RBC) Count": "x10^12/L",
        "Haemoglobin": "g/L",
        "Hematocrit (HCT)": "%",
        "Platelet Count": "x10^9/L",
        "Mean Corpuscular Volume (MCV)": "fL",
        "Mean Corpuscular Hemoglobin (MCH)": "pg",
        "Mean Corpuscular Hemoglobin Concentration (MCHC)": "g/dL",
        "Red Cell Distribution Width (RDW)": "%",
        "Neutrophils": "x10^9/L",
        "Lymphocytes": "x10^9/L",
        "Monocytes": "x10^9/L",
        "Eosinophils": "x10^9/L",
        "Basophils": "x10^9/L",
        "MPV": "fL",
        
        # Thyroid Function
        "TSH (Thyroid Stimulating Hormone)": "mIU/L",
        "Free T4": "pmol/L",
        "Free T3": "pmol/L",
        
        # Inflammation Markers
        "C-Reactive Protein (CRP)": "mg/L",
        "Erythrocyte Sedimentation Rate (ESR)": "mm/hr",
        "hsCRP": "mg/L",
        "Homocysteine (Fasting)": "µmol/L",
        
        # Vitamins and Minerals
        "Vitamin D": "nmol/L",
        "Vitamin B12": "pmol/L",
        "Folate": "ng/mL",
        "Ferritin": "µg/L",
        "Iron": "µmol/L",
        "Transferrin": "g/L",
        "Transferrin Saturation": "%",
        
        # Hormones
        "Follicle Stimulating Hormone": "IU/L",
        "Luteinizing Hormone": "IU/L",
        "Testosterone": "nmol/L",
        "Estradiol": "pmol/L",
        "Prolactin": "mIU/L",
        "Progesterone": "nmol/L",
        "Serum Cortisol": "nmol/L",
        "DHEA-Sulphate": "µmol/L",
        "Free Testosterone": "pmol/L",
        "SHBG (Sex Hormone Binding Globulin)": "nmol/L",
        "Insulin-Like Growth Factor": "nmol/L",
        "Insulin (Fasting)": "mU/L",
        
        # Fatty Acids
        "Total Saturated": "%",
        "Total Monounsaturated": "%",
        "Total n3": "%",
        "Total n6": "%",
        "Ratio n3:n6": "ratio",
        "Ratio AA:EPA": "ratio",
        "Myristic Acid (C14:0)": "%",
        "Palmitic Acid (C16:0)": "%",
        "Stearic Acid (C18:0)": "%",
        "Arachidic Acid (C20:0)": "%",
        "Behenic Acid (C22:0)": "%",
        "Palmitoleic Acid (C16:1n7)": "%",
        "Oleic Acid (C18:1n9)": "%",
        "Gondoic Acid (C20:1n9)": "%",
        "Linoleic Acid (C18:2n6)": "%",
        "Gamma Linolenic Acid (C18:3n6)": "%",
        "Eicosadienoic Acid (C20:2n6)": "%",
        "Eicosatrienoic Acid (C20:3n6)": "%",
        "Arachidonic Acid (C20:4n6)": "%",
        "Alpha Linolenic Acid (C18:3n3)": "%",
        "Eicosapentaenoic Acid (C20:5n3)": "%",
        "Docosapentaenoic Acid (C22:5n3)": "%",
        "Docosahexaenoic Acid (C22:6n3)": "%",
    }
    
    # Get all biomarkers from the database
    biomarkers = dal.get_all_biomarkers()
    print(f"Found {len(biomarkers)} biomarkers in the database.")
    
    # Initialize counters
    updated_count = 0
    skipped_count = 0
    not_found_count = 0
    not_found_biomarkers = []
    
    # Update each biomarker
    for biomarker in biomarkers:
        biomarker_id = biomarker['id']
        biomarker_name = biomarker['name']
        biomarker_category = biomarker['category']
        current_unit = biomarker['unit']
        
        # Check if the biomarker is in our dictionary
        if biomarker_name in biomarker_units:
            new_unit = biomarker_units[biomarker_name]
            
            # Check if the unit needs to be updated
            if current_unit != new_unit:
                # Update the biomarker unit
                success = dal.update_biomarker(biomarker_id, biomarker_name, new_unit, biomarker_category)
                if success:
                    updated_count += 1
                    print(f"Updated unit for {biomarker_name}: {current_unit} -> {new_unit}")
                else:
                    print(f"Failed to update unit for {biomarker_name}")
            else:
                skipped_count += 1
                print(f"Skipped {biomarker_name} (unit already correct: {current_unit})")
        else:
            not_found_count += 1
            not_found_biomarkers.append(biomarker_name)
            print(f"Biomarker not found in unit dictionary: {biomarker_name}")
    
    # Print summary
    print("\nSummary:")
    print(f"Total biomarkers: {len(biomarkers)}")
    print(f"Updated: {updated_count}")
    print(f"Skipped (already correct): {skipped_count}")
    print(f"Not found in unit dictionary: {not_found_count}")
    
    if not_found_count > 0:
        print("\nBiomarkers not found in unit dictionary:")
        for biomarker_name in not_found_biomarkers:
            print(f"- {biomarker_name}")
    
    print("\nUnit update complete.")

if __name__ == "__main__":
    update_biomarker_units()
