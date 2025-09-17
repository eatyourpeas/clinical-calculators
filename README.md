# clinical-calculators

This project standardises all clinical calculators. It is a python project that is both an executable, can be pip installed or can be run as an API (such as a plug-in to FastAPI)

Each calculator occupies a single file in a calculators folder.

## Standardisation

All calculators are standardised in that the top of the file (above all imports) contains docstrings that define all input parameters and the structure of the outputs in .toml.

For example, for a calculator that returns BMI the calculator file might be:

>BMI.py

```python
""""
# BMI Calculator Configuration (TOML Format)
# =======================================

[inputs]
name = "bmi"
purpose = "Calculate Body Mass Index (BMI) based on height and weight."
category = "Anthropometry"

# Input parameters
weight = {
    type = "number",
    required = true,
    unit = "kg",
    description = "Weight in kilograms (mandatory)",
    min = 0,
    max = 250
}

height = {
    type = "number",
    required = true,
    unit = "m",
    description = "Height in meters (mandatory)",
    min = 0.5,
    max = 2.1
}

unit_system = {
    type = "string",
    required = false,
    default = "metric",
    options = ["metric", "imperial"],
    description = "Unit system: 'metric' (default), or 'imperial' (weight in lbs, height in inches)"
}

age = {
    type = "number",
    required = false,
    description = "Optional age for contextual analysis (not used in BMI calculation)"
}

# Validation rules
validations = {
    "weight" = { min = 0, max = 250 },
    "height" = { min = 0.5, max = 2.1 },
    "unit_system" = { allowed_values = ["metric", "imperial"] }
}

# Dependencies
dependencies = [
    "scipy"  # Optional: if used for advanced analysis (e.g., BMI vs age trends)
]

# Output structure
[outputs]
result = {
    type = "number",
    description = "Calculated BMI (kg/m²)",
    example = 22.86
}

working = {
    type = "string",
    description = "Step-by-step explanation of the calculation",
    example = "BMI = weight / (height²) = 70 / (1.75²) = 70 / 3.0625 = 22.86"
}

reference = {
    type = "string",
    description = "Source of BMI formula and classification",
    example = "World Health Organization (2023). Body Mass Index (BMI) classification"
}

methodology = {
    type = "string",
    description = "Formula used: weight (kg) / height (m)²",
    example = "weight (kg) / height (m)²"
}

metadata = {
    type = "object",
    fields = {
        date = { type = "string", format = "iso8601", example = "2024-04-05T10:30:00Z" },
        version = { type = "string", default = "1.0" },
        author = { type = "string", example = "Clinical Computing Team" },
        source = { type = "string", example = "WHO guidelines on BMI classification" }
    }
}

# Interpretations (for downstream use)
interpretation_lay = {
    type = "string",
    example = "This BMI is within the normal range"
}

interpretation_clinician = {
    type = "string",
    example = "This BMI is within the normal range"
}

# Examples
examples = """
>>> bmi = BMI(weight=70, height=1.75, unit_system='metric')
>>> print(bmi.calculate())
{
    "result": 22.86,
    "working": "BMI = weight / (height²) = 70 / (1.75²) = 70 / 3.0625 = 22.86",
    "reference": "World Health Organization (2023). Body Mass Index (BMI) classification",
    "metadata": {
        "date": "2024-04-05T10:30:00Z",
        "version": "1.0",
        "author": "Clinical Computing Team"
    }
}
"""

# Notes and warnings
notes = [
    "BMI does not account for body composition or muscle mass.",
    "For clinical use, consult a physician.",
    "This calculation does not include body fat percentage or lean mass."
]

# Metadata
version = "1.0"
author = "Clinical Computing Team"
date_generated = "2024-04-05"
source = "World Health Organization (2023)"
""""
```

Outputs should include the result, units (if applicable), any references, any interpretation if relevant (one for clinicians, another for lay people), working.

Metadata should include the date and time of request, language, IP address if relevant.

Each calculator has a name that identifies it in the CLI/API/package and have parameters defined in the docstrings. 

## Validation

Validation is compatible with FastAPI and fast API request and response classes for easy integration with APIs

## Instantiation

Whichever way the calculator is accessed, the requests and responses follow the same pattern - all inputs are validated against the structure provided in the .toml defined in the calculator file. There is a cli folder, an api folder and a `main.py`

## Useage

Calling each function should involve only a single function call, with the parameters as defined in the docstring of the relevant calculator file. The response similarly should follow the same structure as defined in the .toml coupled with the metadata which are generic to all requests.

## Documentation

The documentation is created automatically from the docstrings in each file. Documentation is in markdown with one file per calculator in a docs folder. There is separately a folder for contributers which  includes an explainer on how to create a single file calculator, in particular how to scaffold the docstring. There is documentation also for implementors, with a section for each implementer type (API, python package, CLI).

## Testing

Testing is done with pytest. There is a separate folder of unittests, with one file for each calculator.

## Dependencies

These are defined in the docstrings but would need adding to `requirements.txt`. There are base dependencies for all calculators that include pytest, and pydoc/sphinx/mypy for docstring parsing.