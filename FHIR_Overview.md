# Understanding FHIR

FHIR (Fast Healthcare Interoperability Resources) is a standard created by the health-care organization HL7 to help different systems share medical information in a consistent way. Think of it like a common language that apps and hospitals can use to talk to each other about patient data.

## Why it Matters

Healthcare providers, insurance companies, and patients all use many different computer systems. Without a common format, it's very hard to exchange data safely and accurately. FHIR solves this by defining small building blocks called **resources**. Each resource describes a single type of information such as a patient, a coverage plan, or a medical claim.

## How FHIR Data Looks

FHIR data is usually sent in JSON (a text format) or XML. Here is a simplified example of what a Patient resource might look like in JSON:

```json
{
  "resourceType": "Patient",
  "id": "123",
  "name": [{"family": "Smith", "given": ["John"]}],
  "gender": "male",
  "birthDate": "1980-05-15"
}
```

Every resource has required fields (like `resourceType`) and optional ones. By combining resources, systems can describe complex healthcare information in a uniform way.

## FHIR in This Project

The helper functions in `fhir_conversion.py` take raw Availity data and produce three common FHIR resources:

- **Coverage** – details about a patient's insurance plan
- **Claim** – the services submitted for payment
- **ExplanationOfBenefit** – the response showing what was paid or denied

By returning FHIR-formatted dictionaries, these functions make it easier to plug Availity data into other healthcare software that understands FHIR.

## Learn More

FHIR is an open standard with extensive documentation available on [hl7.org/fhir](https://www.hl7.org/fhir/). While the full specification is geared toward developers, the core idea is straightforward: break healthcare information into small pieces (resources) that everyone understands, so data can move smoothly between systems.
