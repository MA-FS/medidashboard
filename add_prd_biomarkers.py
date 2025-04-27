#!/usr/bin/env python3
"""
add_prd_biomarkers.py - Script to add biomarkers from the PRD document to the MediDashboard database.

This script removes all existing biomarkers from the database and adds the
biomarkers from the PRD document with their appropriate units and categories.
"""

import sys
import os

# Add the parent directory to the Python path so we can import the app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import dal

def add_prd_biomarkers():
    """
    Adds biomarkers from the PRD document to the database.
    
    This function:
    1. Removes all existing biomarkers from the database
    2. Adds the biomarkers from the PRD document with their appropriate units and categories
    3. Prints a summary of the operations performed
    """
    print("Adding biomarkers from the PRD document...")
    
    # Get all existing biomarkers
    existing_biomarkers = dal.get_all_biomarkers()
    print(f"Found {len(existing_biomarkers)} existing biomarkers.")
    
    # Delete all existing biomarkers
    deleted_count = 0
    for biomarker in existing_biomarkers:
        biomarker_id = biomarker['id']
        biomarker_name = biomarker['name']
        success = dal.delete_biomarker(biomarker_id)
        if success:
            deleted_count += 1
            print(f"Deleted biomarker: {biomarker_name} (ID: {biomarker_id})")
        else:
            print(f"Failed to delete biomarker: {biomarker_name} (ID: {biomarker_id})")
    
    print(f"Deleted {deleted_count} out of {len(existing_biomarkers)} biomarkers.")
    
    # Define the biomarkers from the PRD document
    prd_biomarkers = [
        # Lipid Profile
        ("Total Cholesterol", "mg/dL", "Lipid Profile"),
        ("HDL Cholesterol", "mg/dL", "Lipid Profile"),
        ("LDL Cholesterol", "mg/dL", "Lipid Profile"),
        ("Non-HDL Cholesterol", "mg/dL", "Lipid Profile"),
        ("Triglycerides", "mg/dL", "Lipid Profile"),
        ("LDL/HDL Ratio", "ratio", "Lipid Profile"),
        ("Chol/HDL Ratio", "ratio", "Lipid Profile"),
        ("Triglyceride / HDL Ratio", "ratio", "Lipid Profile"),
        ("VLDL", "mg/dL", "Lipid Profile"),
        ("Total LDL", "mg/dL", "Lipid Profile"),
        ("Total IDL", "mg/dL", "Lipid Profile"),
        ("Total Small Dense LDL", "mg/dL", "Lipid Profile"),
        ("Small Dense LDL 3", "mg/dL", "Lipid Profile"),
        ("Small Dense LDL 4", "mg/dL", "Lipid Profile"),
        ("Small Dense LDL 5", "mg/dL", "Lipid Profile"),
        ("Small Dense LDL 6", "mg/dL", "Lipid Profile"),
        ("Small Dense LDL 7", "mg/dL", "Lipid Profile"),
        ("Mean Size", "nm", "Lipid Profile"),
        ("Apolipoprotein B", "mg/dL", "Lipid Profile"),
        ("Lipoprotein (a)", "mg/dL", "Lipid Profile"),
        
        # Blood Sugar Levels
        ("Glucose (Fasting)", "mg/dL", "Blood Sugar Levels"),
        ("DCCT HbA1c", "%", "Blood Sugar Levels"),
        ("IFCC HbA1c", "mmol/mol", "Blood Sugar Levels"),
        ("Estimated Avg Glucose", "mg/dL", "Blood Sugar Levels"),
        
        # Kidney Function
        ("Creatinine", "mg/dL", "Kidney Function"),
        ("eGFR", "mL/min/1.73m²", "Kidney Function"),
        ("BUN (Blood Urea Nitrogen)", "mg/dL", "Kidney Function"),
        ("Uric Acid", "mg/dL", "Kidney Function"),
        
        # Liver Function
        ("AST (SGOT)", "U/L", "Liver Function"),
        ("ALT (SGPT)", "U/L", "Liver Function"),
        ("Globulin", "g/dL", "Liver Function"),
        ("ALP (Alkaline Phosphatase)", "U/L", "Liver Function"),
        ("Bilirubin (Total)", "mg/dL", "Liver Function"),
        ("Bilirubin (Direct)", "mg/dL", "Liver Function"),
        ("Bilirubin (Indirect)", "mg/dL", "Liver Function"),
        ("Gamma GT", "U/L", "Liver Function"),
        ("Total Protein", "g/dL", "Liver Function"),
        ("Albumin", "g/dL", "Liver Function"),
        
        # Electrolytes
        ("Sodium", "mmol/L", "Electrolytes"),
        ("Potassium", "mmol/L", "Electrolytes"),
        ("Chloride", "mmol/L", "Electrolytes"),
        ("Calcium", "mg/dL", "Electrolytes"),
        ("Adjusted Calcium", "mg/dL", "Electrolytes"),
        ("Phosphate", "mg/dL", "Electrolytes"),
        ("Magnesium", "mg/dL", "Electrolytes"),
        ("Bicarbonate", "mmol/L", "Electrolytes"),
        ("Anion Gap", "mmol/L", "Electrolytes"),
        
        # Complete Blood Count (CBC)
        ("White Blood Cell (WBC) Count", "cells/μL", "Complete Blood Count (CBC)"),
        ("Red Blood Cell (RBC) Count", "cells/μL", "Complete Blood Count (CBC)"),
        ("Haemoglobin", "g/dL", "Complete Blood Count (CBC)"),
        ("Hematocrit (HCT)", "%", "Complete Blood Count (CBC)"),
        ("Platelet Count", "cells/μL", "Complete Blood Count (CBC)"),
        ("Mean Corpuscular Volume (MCV)", "fL", "Complete Blood Count (CBC)"),
        ("Mean Corpuscular Hemoglobin (MCH)", "pg", "Complete Blood Count (CBC)"),
        ("Mean Corpuscular Hemoglobin Concentration (MCHC)", "g/dL", "Complete Blood Count (CBC)"),
        ("Red Cell Distribution Width (RDW)", "%", "Complete Blood Count (CBC)"),
        ("Neutrophils", "%", "Complete Blood Count (CBC)"),
        ("Lymphocytes", "%", "Complete Blood Count (CBC)"),
        ("Monocytes", "%", "Complete Blood Count (CBC)"),
        ("Eosinophils", "%", "Complete Blood Count (CBC)"),
        ("Basophils", "%", "Complete Blood Count (CBC)"),
        ("MPV", "fL", "Complete Blood Count (CBC)"),
        
        # Thyroid Function
        ("TSH (Thyroid Stimulating Hormone)", "mIU/L", "Thyroid Function"),
        ("Free T4", "ng/dL", "Thyroid Function"),
        ("Free T3", "pg/mL", "Thyroid Function"),
        
        # Inflammation Markers
        ("C-Reactive Protein (CRP)", "mg/L", "Inflammation Markers"),
        ("Erythrocyte Sedimentation Rate (ESR)", "mm/hr", "Inflammation Markers"),
        ("hsCRP", "mg/L", "Inflammation Markers"),
        ("Homocysteine (Fasting)", "μmol/L", "Inflammation Markers"),
        
        # Vitamins and Minerals
        ("Vitamin D", "ng/mL", "Vitamins and Minerals"),
        ("Vitamin B12", "pg/mL", "Vitamins and Minerals"),
        ("Folate", "ng/mL", "Vitamins and Minerals"),
        ("Ferritin", "ng/mL", "Vitamins and Minerals"),
        ("Iron", "μg/dL", "Vitamins and Minerals"),
        ("Transferrin", "mg/dL", "Vitamins and Minerals"),
        ("Transferrin Saturation", "%", "Vitamins and Minerals"),
        
        # Hormones
        ("Follicle Stimulating Hormone", "mIU/mL", "Hormones"),
        ("Luteinizing Hormone", "mIU/mL", "Hormones"),
        ("Testosterone", "ng/dL", "Hormones"),
        ("Estradiol", "pg/mL", "Hormones"),
        ("Prolactin", "ng/mL", "Hormones"),
        ("Progesterone", "ng/mL", "Hormones"),
        ("Serum Cortisol", "μg/dL", "Hormones"),
        ("DHEA-Sulphate", "μg/dL", "Hormones"),
        ("Free Testosterone", "pg/mL", "Hormones"),
        ("SHBG (Sex Hormone Binding Globulin)", "nmol/L", "Hormones"),
        ("Insulin-Like Growth Factor", "ng/mL", "Hormones"),
        ("Insulin (Fasting)", "μIU/mL", "Hormones"),
        
        # Fatty Acids
        ("Total Saturated", "%", "Fatty Acids"),
        ("Total Monounsaturated", "%", "Fatty Acids"),
        ("Total n3", "%", "Fatty Acids"),
        ("Total n6", "%", "Fatty Acids"),
        ("Ratio n3:n6", "ratio", "Fatty Acids"),
        ("Ratio AA:EPA", "ratio", "Fatty Acids"),
        ("Myristic Acid (C14:0)", "%", "Fatty Acids"),
        ("Palmitic Acid (C16:0)", "%", "Fatty Acids"),
        ("Stearic Acid (C18:0)", "%", "Fatty Acids"),
        ("Arachidic Acid (C20:0)", "%", "Fatty Acids"),
        ("Behenic Acid (C22:0)", "%", "Fatty Acids"),
        ("Palmitoleic Acid (C16:1n7)", "%", "Fatty Acids"),
        ("Oleic Acid (C18:1n9)", "%", "Fatty Acids"),
        ("Gondoic Acid (C20:1n9)", "%", "Fatty Acids"),
        ("Linoleic Acid (C18:2n6)", "%", "Fatty Acids"),
        ("Gamma Linolenic Acid (C18:3n6)", "%", "Fatty Acids"),
        ("Eicosadienoic Acid (C20:2n6)", "%", "Fatty Acids"),
        ("Eicosatrienoic Acid (C20:3n6)", "%", "Fatty Acids"),
        ("Arachidonic Acid (C20:4n6)", "%", "Fatty Acids"),
        ("Alpha Linolenic Acid (C18:3n3)", "%", "Fatty Acids"),
        ("Eicosapentaenoic Acid (C20:5n3)", "%", "Fatty Acids"),
        ("Docosapentaenoic Acid (C22:5n3)", "%", "Fatty Acids"),
        ("Docosahexaenoic Acid (C22:6n3)", "%", "Fatty Acids"),
    ]
    
    # Add the biomarkers from the PRD document
    added_count = 0
    for name, unit, category in prd_biomarkers:
        biomarker_id = dal.add_biomarker(name, unit, category)
        if biomarker_id is not None:
            added_count += 1
            print(f"Added biomarker: {name} (ID: {biomarker_id})")
        else:
            print(f"Failed to add biomarker: {name}")
    
    print(f"Added {added_count} out of {len(prd_biomarkers)} biomarkers.")
    print("Biomarker addition complete.")

if __name__ == "__main__":
    add_prd_biomarkers()
