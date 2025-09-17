# clinical-calculators

This project standardises all clinical calculators. It is a python project that is both an executable, can be pip installed or can be run as an API (such as a plug-in to FastAPI)

Each calculator occupies a single file in a calculators folder.

## Run with Docker

- Build the image

```bash
docker build -t clinical-calculators:latest .
```

- Run the API

```bash
docker run --rm -p 8000:8000 clinical-calculators:latest
```

API will be at <http://localhost:8000> (docs at /docs).

- Run in development with hot reload

```bash
docker compose up --build
```

- Use the CLI inside the container

```bash
docker run --rm clinical-calculators:latest calc list
docker run --rm clinical-calculators:latest calc run bmi --params '{"weight":70,"height":1.75,"unit_system":"metric"}'
```

### Dev helper script

To manage Docker in development, use:

```bash
./s/dev.sh up      # build and start in background
./s/dev.sh logs    # follow logs
./s/dev.sh rebuild # rebuild image and restart
./s/dev.sh down    # stop containers
```


## Standardisation

All calculators are standardised in the top of the file (above all imports) with docstrings that define all input parameters and the structure of the outputs in .toml.

### CalculatorRequest Base Class

All calculator request models should subclass the generic `CalculatorRequest` base class, defined in `core/request/request.py`. This provides a consistent structure for request models and a place for shared logic or metadata. Each calculator should define its own fields and validation logic by subclassing `CalculatorRequest`.

#### Example (BMI):

```python
from core.request.request import CalculatorRequest
from pydantic import Field, root_validator

class BMIRequest(CalculatorRequest):
  unit_system: Literal["", "lb/in2"]
  weight: float = Field(..., gt=0, description="Weight in kg or lb (UCUM)")
  height: float = Field(..., gt=0, description="Height in m or in (UCUM)")
  # ...validators...
```

This ensures all calculators have a standard request structure, while allowing for custom fields and validation.

### UCUM Codes for Units

All units should use [UCUM](https://ucum.org/trac) codes for clarity and interoperability. For example:

- Weight: `kg` (UCUM: `kg`), `lb` (UCUM: `[lb_av]`)
- Height: `m` (UCUM: `m`), `in` (UCUM: `[in_i]`)
- Unit system: `metric` for metric, `imperial` for imperial

This standardization ensures compatibility with healthcare and scientific systems.

For example, for a calculator that returns BMI the calculator file might be:

>BMI.py

```python
"""
# BMI Calculator

## 📂 Configuration (TOML-style in docstring)

[inputs]
- name: weight
  type: number
  unit: kg | lb
  required: true
  min: 0.0
  max: 500.0
  description: Patient's weight (in kg or lb)

- name: height
  type: number
  unit: m | in
  required: true
  min: 0.0
  max: 3.0
  description: Patient's height (in meters or inches)

- name: unit_system
  type: string
  enum: ["metric", "imperial"]
  required: true
  description: Unit system for input (metric or imperial)

[dependencies]
  scipy

## 📂 Output (TOML-style)

[result]
  type: number
  description: BMI (rounded to 2 decimals)

[working]
  type: string
  description: Step-by-step calculation

[interpretation]
  type: string
  enum: ["Underweight", "Normal", "Overweight", "Obese"]
  description: WHO-based classification

[reference]
  type: string
  default: "WHO 2023 Guidelines"

[metadata]
  type: object
  fields:
    timestamp: string (ISO8601)
    version: string (e.g., "1.0")
    calculator_name: string

## 📂 Validation Rules
- Height must be > 0 and ≤ 3 m (or 78 in)
- Weight must be > 0 and ≤ 500 kg (or 1100 lb)
- unit_system must be one of: metric, imperial

## 📂 Usage (CLI or API)

CLI: 
  bmi --weight 70 --height 1.75 --unit-system metric

API:
  POST /calculate
  {
    "calculator": "bmi",
    "params": {
      "weight": 70,
      "height": 1.75,
      "unit_system": "metric"
    }
  }

## 📂 Output Example
{
  "result": 24.69,
  "working": "Weight: 70.0 kg, Height: 1.75 m → BMI = 24.69",
  "interpretation": "Normal",
  "reference": "WHO 2023",
  "metadata": {
    "timestamp": "2025-04-05T10:00:00Z",
    "version": "1.0",
    "calculator_name": "bmi"
  }
}

"""
```


## 📂 Standardised Response Model

All calculators return a response using the generic `CalculationResponse` class, defined in `core/response/response.py`. This Pydantic model is used by all calculators to ensure a consistent API, CLI, and package interface.

### CalculationResponse fields

- `result`: The main result of the calculation (type: any)
- `working`: Step-by-step calculation or details (type: dict or string)
- `interpretation`: Interpretation of the result (e.g., clinical meaning)
- `reference`: Reference or source for the calculation (e.g., guidelines)
- `metadata`: Additional metadata (timestamp, version, calculator_name, etc.)

Example usage in a calculator:

```python
from core.response.response import CalculationResponse

def calculate(params: ...):
  # ... calculation logic ...
  return CalculationResponse(
    result=...,  # main result
    working=...,  # step-by-step or details
    interpretation=...,  # clinical meaning
    reference="...",  # source or guideline
    metadata={...},  # extra info
  )
```

This ensures all calculators have a standard output structure, making integration and usage consistent across API, CLI, and as a Python package.

Metadata should include the date and time of request, language, and any other relevant context.

Each calculator has a name that identifies it in the CLI/API/package and has parameters defined in the docstrings.

## Structure

```text
clinical-calculators/
│
├── calculators/                    # One file per calculator (e.g., bmi.py, ifcc_to_dcct.py)
│   ├── bmi.py
│   ├── ifcc_to_dcct.py
│   └── ...
│
├── core/                          # Shared logic
│   ├── calculator.py             # Base class with config loading
│   ├── loader.py                 # Load by name, read config
│   └── metadata.py               # Versioning, metadata handling
│
├── cli/                          # CLI entry point
│   ├── main.py
│   └── templates/               # CLI templates (optional)
│
├── api/                         # FastAPI server
│   ├── main.py
│   └── schemas/                 # Pydantic models (auto-generated from config)
│
├── tests/                       # Unit & integration tests
│   └── test_calculator.py
│
├── docs/                        # Auto-generated docs (from docstrings + config)
│
├── pyproject.toml
├── setup.py
└── README.md
```

## Templates

The project includes templates with form templates for each field in basic jinja that can be used whichever

## Validation

Validation is compatible with FastAPI and fast API request and response classes for easy integration with APIs. These Validation classes are specific to each calculator and referenced in the TOML at the top of each calculator file and defined in the same file.

## Instantiation

Whichever way the calculator is accessed (API/pip install or CLI), the requests and responses follow the same pattern - all inputs are validated against the structure provided in the .toml using the FastAPI Response and Request classes defined in the calculator file. There is a cli folder, an api folder and a `main.py`

## Useage

Calling each function should involve only a single function call, with the parameters as defined in the docstring of the relevant calculator file. The response similarly should follow the same structure as defined in the .toml coupled with the metadata which are generic to all requests.

## Documentation

The documentation is created automatically from the docstrings in each file. Documentation is in markdown with one file per calculator in a docs folder. There is separately a folder for contributers which  includes an explainer on how to create a single file calculator, in particular how to scaffold the docstring. There is documentation also for implementors, with a section for each implementer type (API, python package, CLI).

## Testing

Testing is done with pytest. There is a separate folder of unittests, with one file for each calculator.

## Dependencies

These are defined in the docstrings but would need adding to `requirements.txt`. There are base dependencies for all calculators that include pytest, and pydoc/sphinx/mypy for docstring parsing.

## Creating a new calculator

Use the BMI file as an example

1. create a new file in the calculators folder
2. Create a .toml docstring at the top of the file - this defines the inputs and the outputs
3. Create a FastAPI pydantic Request and Response class containing any custom validators. The Response class must have the same keys as the CalculatorResponse class. The request class must override the CalculatorRequest class. The units (if required) should reference the [UCUM](https://ucum.org/docs) standard.
4. Define a `calculate` function
5. Create some tests in the `tests` folder

## Using the calculator

The project is dockerised so can be run with:
`s/dev.sh up`

### Using the API
