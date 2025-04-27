#!/usr/bin/env python3
"""
reset_biomarkers.py - Script to reset biomarkers in the MediDashboard database.

This script removes all existing biomarkers from the database and adds the
standard biomarkers from the PRD document.
"""

import sys
import os

# Add the parent directory to the Python path so we can import the app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import dal

def reset_biomarkers():
    """
    Resets the biomarkers in the database by removing all existing biomarkers
    and adding the standard biomarkers from the PRD document.
    """
    print("Resetting biomarkers in the database...")

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

    # Define the comprehensive list of biomarkers from the PRD document
    initial_biomarkers = [
        # Blood biomarkers
        ("Hemoglobin", "g/dL", "Blood"),
        ("Hematocrit", "%", "Blood"),
        ("White Blood Cell Count", "cells/μL", "Blood"),
        ("Platelet Count", "cells/μL", "Blood"),
        ("Red Blood Cell Count", "cells/μL", "Blood"),
        ("Mean Corpuscular Volume", "fL", "Blood"),
        ("Mean Corpuscular Hemoglobin", "pg", "Blood"),
        ("Mean Corpuscular Hemoglobin Concentration", "g/dL", "Blood"),
        ("Red Cell Distribution Width", "%", "Blood"),
        ("Neutrophils", "%", "Blood"),
        ("Lymphocytes", "%", "Blood"),
        ("Monocytes", "%", "Blood"),
        ("Eosinophils", "%", "Blood"),
        ("Basophils", "%", "Blood"),

        # Lipid biomarkers
        ("Total Cholesterol", "mg/dL", "Lipids"),
        ("HDL Cholesterol", "mg/dL", "Lipids"),
        ("LDL Cholesterol", "mg/dL", "Lipids"),
        ("Triglycerides", "mg/dL", "Lipids"),
        ("VLDL Cholesterol", "mg/dL", "Lipids"),
        ("Total Cholesterol/HDL Ratio", "ratio", "Lipids"),
        ("Non-HDL Cholesterol", "mg/dL", "Lipids"),
        ("Apolipoprotein A1", "mg/dL", "Lipids"),
        ("Apolipoprotein B", "mg/dL", "Lipids"),
        ("Lipoprotein(a)", "mg/dL", "Lipids"),

        # Metabolic biomarkers
        ("Glucose (Fasting)", "mg/dL", "Metabolic"),
        ("HbA1c", "%", "Metabolic"),
        ("Insulin", "μIU/mL", "Metabolic"),
        ("C-Peptide", "ng/mL", "Metabolic"),
        ("HOMA-IR", "value", "Metabolic"),
        ("Glucose (Random)", "mg/dL", "Metabolic"),
        ("Glucose (2-hour postprandial)", "mg/dL", "Metabolic"),

        # Liver biomarkers
        ("ALT", "U/L", "Liver"),
        ("AST", "U/L", "Liver"),
        ("Alkaline Phosphatase", "U/L", "Liver"),
        ("Total Bilirubin", "mg/dL", "Liver"),
        ("Direct Bilirubin", "mg/dL", "Liver"),
        ("Indirect Bilirubin", "mg/dL", "Liver"),
        ("Gamma-Glutamyl Transferase", "U/L", "Liver"),
        ("Albumin", "g/dL", "Liver"),
        ("Total Protein", "g/dL", "Liver"),

        # Kidney biomarkers
        ("Creatinine", "mg/dL", "Kidney"),
        ("BUN", "mg/dL", "Kidney"),
        ("eGFR", "mL/min/1.73m²", "Kidney"),
        ("BUN/Creatinine Ratio", "ratio", "Kidney"),
        ("Uric Acid", "mg/dL", "Kidney"),
        ("Cystatin C", "mg/L", "Kidney"),
        ("Microalbumin", "mg/L", "Kidney"),
        ("Urinary Albumin-to-Creatinine Ratio", "mg/g", "Kidney"),

        # Electrolytes
        ("Sodium", "mmol/L", "Electrolytes"),
        ("Potassium", "mmol/L", "Electrolytes"),
        ("Chloride", "mmol/L", "Electrolytes"),
        ("Calcium", "mg/dL", "Electrolytes"),
        ("Magnesium", "mg/dL", "Electrolytes"),
        ("Phosphorus", "mg/dL", "Electrolytes"),
        ("Bicarbonate", "mmol/L", "Electrolytes"),
        ("Anion Gap", "mmol/L", "Electrolytes"),

        # Vitamins and Minerals
        ("Vitamin D", "ng/mL", "Vitamins"),
        ("Vitamin B12", "pg/mL", "Vitamins"),
        ("Folate", "ng/mL", "Vitamins"),
        ("Vitamin A", "μg/dL", "Vitamins"),
        ("Vitamin E", "mg/L", "Vitamins"),
        ("Vitamin K", "ng/mL", "Vitamins"),
        ("Iron", "μg/dL", "Minerals"),
        ("Ferritin", "ng/mL", "Minerals"),
        ("Zinc", "μg/dL", "Minerals"),
        ("Copper", "μg/dL", "Minerals"),
        ("Selenium", "μg/L", "Minerals"),
        ("Total Iron Binding Capacity", "μg/dL", "Minerals"),
        ("Transferrin", "mg/dL", "Minerals"),
        ("Transferrin Saturation", "%", "Minerals"),

        # Hormones
        ("TSH", "mIU/L", "Hormones"),
        ("Free T4", "ng/dL", "Hormones"),
        ("Free T3", "pg/mL", "Hormones"),
        ("Total T3", "ng/dL", "Hormones"),
        ("Total T4", "μg/dL", "Hormones"),
        ("Cortisol", "μg/dL", "Hormones"),
        ("Estradiol", "pg/mL", "Hormones"),
        ("Progesterone", "ng/mL", "Hormones"),
        ("Testosterone", "ng/dL", "Hormones"),
        ("DHEA-S", "μg/dL", "Hormones"),
        ("Prolactin", "ng/mL", "Hormones"),
        ("FSH", "mIU/mL", "Hormones"),
        ("LH", "mIU/mL", "Hormones"),
        ("Parathyroid Hormone", "pg/mL", "Hormones"),
        ("Growth Hormone", "ng/mL", "Hormones"),
        ("IGF-1", "ng/mL", "Hormones"),

        # Inflammatory markers
        ("C-Reactive Protein", "mg/L", "Inflammation"),
        ("ESR", "mm/hr", "Inflammation"),
        ("Homocysteine", "μmol/L", "Inflammation"),
        ("Fibrinogen", "mg/dL", "Inflammation"),
        ("Interleukin-6", "pg/mL", "Inflammation"),
        ("TNF-alpha", "pg/mL", "Inflammation"),

        # Cardiac markers
        ("Troponin I", "ng/mL", "Cardiac"),
        ("Troponin T", "ng/mL", "Cardiac"),
        ("CK-MB", "ng/mL", "Cardiac"),
        ("BNP", "pg/mL", "Cardiac"),
        ("NT-proBNP", "pg/mL", "Cardiac"),
        ("Myoglobin", "ng/mL", "Cardiac"),

        # Coagulation markers
        ("Prothrombin Time", "seconds", "Coagulation"),
        ("Partial Thromboplastin Time", "seconds", "Coagulation"),
        ("International Normalized Ratio", "ratio", "Coagulation"),
        ("D-dimer", "ng/mL", "Coagulation"),
        ("Fibrinogen", "mg/dL", "Coagulation"),

        # Bone markers
        ("Alkaline Phosphatase (Bone-specific)", "μg/L", "Bone"),
        ("Osteocalcin", "ng/mL", "Bone"),
        ("N-telopeptide", "nmol BCE/L", "Bone"),
        ("C-telopeptide", "ng/L", "Bone"),

        # Autoimmune markers
        ("Antinuclear Antibodies", "titer", "Autoimmune"),
        ("Rheumatoid Factor", "IU/mL", "Autoimmune"),
        ("Anti-CCP Antibodies", "U/mL", "Autoimmune"),
        ("Anti-dsDNA Antibodies", "IU/mL", "Autoimmune"),
        ("Anti-TPO Antibodies", "IU/mL", "Autoimmune"),
        ("Anti-Thyroglobulin Antibodies", "IU/mL", "Autoimmune"),
    ]

    # Add the standard biomarkers
    added_count = 0
    for name, unit, category in initial_biomarkers:
        biomarker_id = dal.add_biomarker(name, unit, category)
        if biomarker_id is not None:
            added_count += 1
            print(f"Added biomarker: {name} (ID: {biomarker_id})")
        else:
            print(f"Failed to add biomarker: {name}")

    print(f"Added {added_count} out of {len(initial_biomarkers)} biomarkers.")
    print("Biomarker reset complete.")

if __name__ == "__main__":
    reset_biomarkers()
