# Body Mass Analysis Across Experimental Groups

Python scripts for analyzing body mass differences between experimental groups across postnatal development.

## Requirements

Install the required Python packages before running the script:

```bash
pip install pandas numpy matplotlib scipy openpyxl
```

## Input Files

The scripts expect Excel files containing body weight measurements across days.

Example from the current script:

* `Pup_Weight.xlsx`
  Main dataset containing body mass measurements for individual animals across postnatal days

## Expected Columns

Your input data should contain:

* `Age` (postnatal day)

All other columns are assumed to represent individual animals (one column per animal).

Column names should include identifiers for:

* experimental group (e.g. control, SD)
* sex (e.g. female/jente, male/gutt)

These are used to automatically group animals.

## Usage

1. Update the file path in the script so it points to your local Excel file.
2. Select which days to include in the analysis (e.g. `[16, 18, 20, 24]`).
3. Run the script in Spyder, VS Code, Jupyter, or from the command line.

## Output

The scripts generate plots such as:

* mean body mass across age (± SEM)
* comparisons between experimental groups (control vs SD)
* comparisons by sex (female vs male)
* combined group averages

Some versions of the script also include:

* body mass normalized to a baseline day (e.g. P16)
* statistical comparisons annotated directly on plots

## Statistical Methods

Depending on sample size and data distribution, the scripts use:

* Shapiro–Wilk test for normality
* Welch’s t-test for normally distributed data
* Mann–Whitney U test for non-normal data
* permutation tests for small sample sizes

## Example Workflow

A typical workflow in these scripts is:

1. Load body mass data from Excel
2. Filter relevant age range
3. Group animals by experimental condition and sex
4. Compute mean and SEM for each group and day
5. Generate bar plots with group comparisons
6. Perform statistical tests between groups

## Notes

* The scripts currently use absolute local file paths. These should be changed before sharing the code.
* Column naming is important, as grouping is based on keywords in column names.
* The scripts assume one column per animal and one row per day.
* Some scripts include both absolute and normalized body mass analyses.

## Author

Solveig Horn
[solhorn4@gmail.com](mailto:solhorn4@gmail.com)
