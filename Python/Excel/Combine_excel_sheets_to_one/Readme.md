# Excel Parser Script

This Python script is designed to read data from an Excel file, process it, and then write the processed data back to a new Excel file. It utilizes the `pandas` library for data manipulation and `openpyxl` for handling Excel files.

## Features

- Reads multiple sheets from an Excel file.
- Extracts specific columns (`CHS`, `ru`, `ID`, `Extra`) from each sheet.
- Writes the extracted data into a new Excel file with a predefined format.

## Prerequisites

Before running the script, ensure you have the following installed:

- Python 3.x
- `pandas` library
- `openpyxl` library

You can install the required libraries using pip:
```
pip install pandas openpyxl
```

Usage
Set the Directory and File Name:

Modify the dir variable to point to the directory where your Excel file is located.

Update the name variable with the name of your Excel file.

Run the Script:

Execute the script using a Python interpreter.

sh
Copy code
python script_name.py
Output:

The script will generate a new Excel file named Project R & Inlingo_TM Update-RU_20240903_output.xlsx in the same directory as the input file.

The output file will contain the extracted data with headers source, target, ID, and Extra.

Script Details
Input File: The script reads an Excel file specified by the dir and name variables.

Data Processing: It iterates through each sheet in the Excel file, extracts the required columns, and appends them to a new worksheet.

Output File: The processed data is saved to a new Excel file with the suffix _output.
