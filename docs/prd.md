
# Detailed Feature List & Configurability

## I. Core Functionality

### Biomarker Definition Management:

* **Add Custom Biomarkers:** Ability to define new biomarkers the user wants to track.¹ Requires specifying:
    * `Biomarker Name` (e.g., "Total Cholesterol", "Resting Heart Rate", "Vitamin D Level"). Must be unique.
    * `Unit of Measurement` (e.g., "mg/dL", "mmol/L", "bpm", "ng/mL").
* **Edit Biomarkers:** Modify the name or unit of an existing biomarker definition. (**Note:** Changing units might require careful consideration of historical data interpretation, though the raw values remain unchanged).
* **Delete Biomarkers:** Remove a biomarker definition. This should likely prompt the user about what happens to associated readings (e.g., delete readings or orphan them – deleting is usually cleaner).
* **View Biomarker List:** A clear overview list of all currently defined biomarkers and their units.

### Biomarker Reading Entry:

* **Add New Reading:** A dedicated, easy-to-access form.² Requires:
    * Selection of the target Biomarker (from the user-defined list).
    * Date and Time of the reading (using a user-friendly date/time picker).
    * Numeric `Value` of the reading.
    * Display of the selected biomarker's unit next to the value input field for context.
* **Input Validation:** Real-time checks to ensure the value entered is numeric and the date/time is valid.⁴
* **Edit Readings:** Ability to correct or modify previously entered readings (value or timestamp).
* **Delete Readings:** Ability to remove individual data points.

### Dashboard & Visualization:

* **Main Dashboard View:** A central screen displaying widgets for tracked biomarkers.⁵
* **Biomarker Widgets:** Each widget dedicated to a specific biomarker, showing:
    * Biomarker Name and Unit.
    * Interactive Time-Series Chart (`Plotly Line Chart`): Visualizing the biomarker's trend over time.¹² Includes features like:
        * Zooming and Panning.
        * Hover Tooltips showing exact value and date/time for data points.
    * Display of the most recent reading's value and date.
    * (Optional) Basic summary statistics (e.g., average, min/max over selected period).
* **Chart Time Range Selection:** Ability to filter the time range displayed on charts (e.g., Last 30 days, Last 6 months, Last year, All time, Custom range).

### Data Management:

* **Local Storage:** All data (biomarker definitions and readings) stored securely in a local `SQLite` database file on the user's computer.¹⁵
* **Backup (Export):** A user-initiated function ("Backup Data") that creates a complete, consistent copy of the `SQLite` database file using the `.backup` command/API.¹⁸ This triggers a browser download, allowing the user to save the backup file (e.g., `BiomarkerBackup_YYYY-MM-DD.db`) to a location of their choice (local drive, USB, cloud-synced folder).
* **Restore (Import):** A user-initiated function ("Restore Data") allowing the user to upload a previously created backup file.
    * **Clear Warning:** Explicitly warns the user that restoring will overwrite current readings and potentially merge biomarker definitions. Requires user confirmation.
    * **Intelligent Biomarker Merging (Handling Discrepancies):**
        * The restore process will replace all current readings with the readings from the backup file.
        * It will then compare the biomarker definitions (Name and Unit) in the backup file against the current definitions in the application.
        * Any biomarker definitions present in the backup file but not currently defined in the application (based on an exact match of Name and Unit) will be added to the application's list of defined biomarkers.
        * Existing biomarker definitions in the application will not be deleted or overwritten if they are not present in the backup file (protecting definitions created since the backup).
        * Biomarker definitions that exist in both the backup and the current application (matching Name and Unit) will remain unchanged.
        * This ensures all data from the backup is restored, new definitions from the backup are incorporated, and definitions created since the backup are preserved.
    * **User Feedback:** Provides a confirmation message upon successful restore, potentially indicating how many readings were restored and if any new biomarker definitions were added.

## II. User Interface & Experience (UI/UX)

* **Intuitive Navigation:** Simple and clear navigation between the main dashboard, data entry forms, and settings pages.²⁰
* **Clean Visual Design:** Mimics Apple design, follow human interface guidelines. Professional look and feel, prioritizing readability and minimizing clutter. Effective use of whitespace.²⁰
* **Responsiveness:** The web interface should adapt gracefully to different browser window sizes.²¹
* **Clear Feedback:** Visual confirmation for actions like saving data, successful backups, or successful restores.²⁰
* **Accessibility Considerations:** Adherence to basic accessibility principles like sufficient color contrast and readable font sizes.²⁰

## III. Configurability Options

### Dashboard Layout:

* Ability to reorder the biomarker widgets on the main dashboard.
* Ability to hide/show specific biomarker widgets.

### Chart Display:

* Option to set a default time range for charts (e.g., always show the last 6 months initially).
* (Advanced) Potential for minor chart appearance tweaks (e.g., toggle markers on/off on line charts).

### Date/Time Formatting:

* Option to select preferred date and time display format (e.g., MM/DD/YYYY vs DD/MM/YYYY, 12hr vs 24hr time).

### Theme:

* Option to switch between a Light Mode and a Dark Mode interface.

### (Future) Reminders/Notifications:

* If implemented, allow configuration of reminder frequency or types.¹

### Initial Biomarker and category dataset:

* **Lipid Profile**
    * Total Cholesterol
    * HDL Cholesterol
    * LDL Cholesterol
    * Non-HDL Cholesterol
    * Triglycerides
    * LDL/HDL Ratio
    * Chol/HDL Ratio
    * Triglyceride / HDL Ratio
    * VLDL
    * Total LDL
    * Total IDL
    * Total Small Dense LDL
    * Small Dense LDL 3
    * Small Dense LDL 4
    * Small Dense LDL 5
    * Small Dense LDL 6
    * Small Dense LDL 7
    * Mean Size
    * Apolipoprotein B
    * Lipoprotein (a)
* **Blood Sugar Levels**
    * Glucose (Fasting)
    * DCCT HbA1c
    * IFCC HbA1c
    * Estimated Avg Glucose
* **Kidney Function**
    * Creatinine
    * eGFR
    * BUN (Blood Urea Nitrogen)
    * Uric Acid
* **Liver Function**
    * AST (SGOT)
    * ALT (SGPT)
    * Globulin
    * ALP (Alkaline Phosphatase)
    * Bilirubin (Total)
    * Bilirubin (Direct)
    * Bilirubin (Indirect)
    * Gamma GT
    * Total Protein
    * Albumin
* **Electrolytes**
    * Sodium
    * Potassium
    * Chloride
    * Calcium
    * Adjusted Calcium
    * Phosphate
    * Magnesium
    * Bicarbonate
    * Anion Gap
* **Complete Blood Count (CBC)**
    * White Blood Cell (WBC) Count
    * Red Blood Cell (RBC) Count
    * Haemoglobin
    * Hematocrit (HCT)
    * Platelet Count
    * Mean Corpuscular Volume (MCV)
    * Mean Corpuscular Hemoglobin (MCH)
    * Mean Corpuscular Hemoglobin Concentration (MCHC)
    * Red Cell Distribution Width (RDW)
    * Neutrophils
    * Lymphocytes
    * Monocytes
    * Eosinophils
    * Basophils
    * MPV
* **Thyroid Function**
    * TSH (Thyroid Stimulating Hormone)
    * Free T4
    * Free T3
* **Inflammation Markers**
    * C-Reactive Protein (CRP)
    * Erythrocyte Sedimentation Rate (ESR)
    * hsCRP
    * Homocysteine (Fasting)
* **Vitamins and Minerals**
    * Vitamin D
    * Vitamin B12
    * Folate
    * Ferritin
    * Iron
    * Transferrin
    * Transferrin Saturation
* **Hormones**
    * Follicle Stimulating Hormone
    * Luteinizing Hormone
    * Testosterone
    * Estradiol
    * Prolactin
    * Progesterone
    * Serum Cortisol
    * DHEA-Sulphate
    * Free Testosterone
    * SHBG (Sex Hormone Binding Globulin)
    * Insulin-Like Growth Factor
    * Insulin (Fasting)
* **Fatty Acids**
    * Total Saturated
    * Total Monounsaturated
    * Total n3
    * Total n6
    * Ratio n3:n6
    * Ratio AA:EPA
    * Myristic Acid (C14:0)
    * Palmitic Acid (C16:0)
    * Stearic Acid (C18:0)
    * Arachidic Acid (C20:0)
    * Behenic Acid (C22:0)
    * Palmitoleic Acid (C16:1n7)
    * Oleic Acid (C18:1n9)
    * Gondoic Acid (C20:1n9)
    * Linoleic Acid (C18:2n6)
    * Gamma Linolenic Acid (C18:3n6)
    * Eicosadienoic Acid (C20:2n6)
    * Eicosatrienoic Acid (C20:3n6)
    * Arachidonic Acid (C20:4n6)
    * Alpha Linolenic Acid (C18:3n3)
    * Eicosapentaenoic Acid (C20:5n3)
    * Docosapentaenoic Acid (C22:5n3)
    * Docosahexaenoic Acid (C22:6n3)
