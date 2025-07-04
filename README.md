# Availity FHIR Conversion Utilities

This repository provides helper functions for converting raw Availity API responses into
[FHIR v4.0.1](https://www.hl7.org/fhir/) compliant resources. The module `fhir_conversion.py`
contains three main functions:

- `convert_eligibility_to_coverage` – converts an eligibility response to a FHIR `Coverage` resource.
- `convert_claim_to_fhir_claim` – converts claim submission data to a FHIR `Claim` resource.
- `convert_eob_to_explanation_of_benefit` – converts ERA or claim status information to a FHIR `ExplanationOfBenefit` resource.

Each function accepts a dictionary of raw Availity data and returns a dictionary that adheres to the FHIR specification.
These utilities can be integrated into a FastAPI or Flask backend to normalize healthcare data.

## Additional Resources

For a plain-language introduction to the FHIR standard, see [FHIR_Overview.md](FHIR_Overview.md).
