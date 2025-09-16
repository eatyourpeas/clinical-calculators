# clinical-calculators

This project standardises all clinical calculators. It is a python project that is both an executable, can be pip installed or can be run as an API (such as a plug-in to FastAPI)

Each calculator occupies a single file in a calculators folder.

## Standardisation

All calculators are standardised in that the top of the file (above all imports) contains docstrings that define all input parameters and the structure of the outputs. The structure of all the inputs and outputs is standardised and defined in a config folder, with an inputs.yaml, outputs.yaml and metadata.yaml. These define the structure that all the inputs and outputs take.

For example, for a calculator that returns BMI the calculator file might be:

>BMI.py

```python
""""
INPUTS
Name: BMI
Purpose:
    Calculate Body Mass Index (BMI) based on height and weight.
Category:
    Anthropometry

 Inputs:
     - weight (float): Weight in kilograms (mandatory)
     - height (float): Height in meters (mandatory)
     - unit_system (str): 'metric' (default), or 'imperial' (weight in lbs, height in inches)
     - age (int): Optional, for contextual analysis (not used in BMI itself)

Validations:
    - weight:
       - max: 250
       - min: 0
    - height:
       - max: 210
       - min: 50
    - unit_system in ['metric', 'imperial']

Dependencies
   - scipy

Outputs:
    - result (float): BMI (kg/m²)
    - working (str): Step-by-step explanation of calculation
    - reference (str): Source of BMI formula (WHO, 2023)
   - methodology:
    - metadata:
        - date: ISO datetime of calculation
        - version: "1.0"
        - author: "Clinical Computing Team"
        - source: "WHO guidelines on BMI classification"

Examples:
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

Note:
    - BMI does not account for body composition or muscle mass.
    - For clinical use, consult a physician.

OUTPUTS

result: 22.86
units: kg/m2
reference: World Health Organisation
methodology: weight (kg) / height (m)^2
working: BMI = weight / (height²) = 70 / (1.75²) = 70 / 3.0625 = 22.86
interpretation_lay: This BMI is within the normal range
interpretation_clinician: This BMI is within the normal range

""""
```

Outputs should include the result, units (if applicable), any references, any interpretation if relevant (one for clinicians, another for lay people), working.

Metadata should include the date and time of request, language, IP address if relevant.

Each calculator has a name that identifies it in the CLI/API/package and have parameters defined in the docstrings, following the structure in the yaml files. 

## Validation

Validation is compatible with FastAPI and fast API request and response classes for easy integration with APIs

## Instantiation

Whichever way the calculator is accessed, the requests and responses follow the same pattern - all inputs are validated against the structure provided in the yaml files using the specific names and inputs defined in the calculator file. There is a cli folder, an api folder and a `main.py`

## Useage

Calling each function should involve only a single function call, with the parameters as defined in the docstring of the relevant calculator file, in the structure defined in the yaml file. The response similarly should follow the same structure as defined in the yaml, using the content from the docstrings, coupled with the metadata which are generic to all requests.

## Documentation

The documentation is created automatically from the docstrings in each file. Documentation is in markdown with one file per calculator in a docs folder. There is separately a folder for contributers which  includes an explainer on how to create a single file calculator, in particular how to scaffold the docstring. There is documentation also for implementors, with a section for each implementer type (API, python package, CLI).

## Testing

Testing is done with pytest. There is a separate folder of unittests, with one file for each calculator.

## Dependencies

These are defined in the docstrings but would need adding to `requirements.txt`. There are base dependencies for all calculators that include pytest, and pydoc/sphinx/mypy for docstring parsing.