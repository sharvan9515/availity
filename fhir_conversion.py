"""Utility functions for converting Availity data into FHIR v4.0.1 resources."""

from typing import Any, Dict, List
from datetime import datetime
import uuid


def convert_eligibility_to_coverage(raw: Dict[str, Any]) -> Dict[str, Any]:
    """Convert Availity eligibility response data to a FHIR Coverage resource.

    Parameters
    ----------
    raw: dict
        Raw eligibility data returned by Availity.

    Returns
    -------
    dict
        FHIR Coverage resource compliant with v4.0.1.
    """
    coverage = {
        "resourceType": "Coverage",
        # Unique identifier for the coverage record
        "id": str(raw.get("coverage_id") or uuid.uuid4()),
        # Coverage status (e.g. active, cancelled)
        "status": raw.get("status", "active"),
        # Reference to the beneficiary (the patient covered)
        "beneficiary": {"reference": f"Patient/{raw.get('beneficiary_id')}"},
        # Reference to the subscriber if different from beneficiary
        "subscriber": {"reference": f"Patient/{raw.get('subscriber_id')}"},
        # Identifier assigned by the payer
        "subscriberId": raw.get("subscriber_id"),
        # The organization providing the coverage
        "payor": [{"display": raw.get("payor_name")}],
    }

    # Optional class/category such as group or plan number
    if raw.get("group_plan"):
        coverage["class"] = [
            {
                "type": {"text": "group"},
                "value": raw["group_plan"],
            }
        ]

    # Optional network identifier
    if raw.get("network"):
        coverage["network"] = raw["network"]

    # Optional copay information
    if raw.get("copay"):
        coverage["costToBeneficiary"] = [
            {
                "type": {"text": "copay"},
                "valueMoney": {
                    "value": raw["copay"],
                    "currency": raw.get("currency", "USD"),
                },
            }
        ]

    return coverage


def convert_claim_to_fhir_claim(raw: Dict[str, Any]) -> Dict[str, Any]:
    """Convert claim submission data to a FHIR Claim resource.

    Parameters
    ----------
    raw: dict
        Raw claim information containing CPT code, NPI, charge, etc.

    Returns
    -------
    dict
        FHIR Claim resource compliant with v4.0.1.
    """
    claim_item = {
        # Sequence number of the service line
        "sequence": 1,
        # CPT or procedure code for the service
        "productOrService": {
            "coding": [{"code": raw.get("cpt_code")}]
        },
        # Charge amount for the service
        "unitPrice": {
            "value": raw.get("charge"),
            "currency": raw.get("currency", "USD"),
        },
    }

    claim = {
        "resourceType": "Claim",
        # Claim status (e.g. active, cancelled)
        "status": raw.get("status", "active"),
        # Indicates how the claim is intended to be processed
        "use": "claim",
        # Type of claim (professional, institutional, etc.)
        "type": {"coding": [{"code": raw.get("claim_type", "professional")}]},
        # Reference to the patient
        "patient": {"reference": f"Patient/{raw.get('patient_id')}"},
        # Date the claim was created
        "created": raw.get("created_date", datetime.utcnow().date().isoformat()),
        # Rendering or billing provider
        "provider": {
            "identifier": {
                "system": "http://hl7.org/fhir/sid/us-npi",
                "value": raw.get("npi"),
            }
        },
        # Priority of the claim (normal by default)
        "priority": {"coding": [{"code": "normal"}]},
        # List of service line items
        "item": [claim_item],
    }

    return claim


def convert_eob_to_explanation_of_benefit(raw: Dict[str, Any]) -> Dict[str, Any]:
    """Convert ERA or claim status information to a FHIR ExplanationOfBenefit.

    Parameters
    ----------
    raw: dict
        Raw EOB or ERA data from Availity.

    Returns
    -------
    dict
        FHIR ExplanationOfBenefit resource compliant with v4.0.1.
    """
    eob = {
        "resourceType": "ExplanationOfBenefit",
        # Current status of the EOB record
        "status": raw.get("status", "active"),
        # The type of EOB (professional, institutional, etc.)
        "type": {"coding": [{"code": raw.get("eob_type", "professional")}]},
        # Reference to the patient for whom services were provided
        "patient": {"reference": f"Patient/{raw.get('patient_id')}"},
        # Creation date of this EOB
        "created": raw.get("created_date", datetime.utcnow().date().isoformat()),
        # Insurer responsible for the claim
        "insurer": {"display": raw.get("insurer_name")},
        # Healthcare provider who submitted the claim
        "provider": {
            "identifier": {
                "system": "http://hl7.org/fhir/sid/us-npi",
                "value": raw.get("npi"),
            }
        },
        # Reference to the original claim
        "claim": {"identifier": {"value": raw.get("claim_id")}},
        # Outcome of processing (complete, partial, etc.)
        "outcome": raw.get("outcome", "complete"),
    }

    # Payment information if present
    if raw.get("payment_amount"):
        eob["payment"] = {
            "amount": {
                "value": raw["payment_amount"],
                "currency": raw.get("currency", "USD"),
            }
        }

    # High-level adjudication results for the entire claim
    adjudication: List[Dict[str, Any]] = []
    if raw.get("charge"):
        adjudication.append(
            {
                "category": {"coding": [{"code": "submitted"}]},
                "amount": {
                    "value": raw["charge"],
                    "currency": raw.get("currency", "USD"),
                },
            }
        )
    if raw.get("allowed_amount"):
        adjudication.append(
            {
                "category": {"coding": [{"code": "allowed"}]},
                "amount": {
                    "value": raw["allowed_amount"],
                    "currency": raw.get("currency", "USD"),
                },
            }
        )
    if adjudication:
        eob["adjudication"] = adjudication

    # Optional line item details
    items_raw = raw.get("items") or []
    if items_raw:
        eob["item"] = []
        for idx, item in enumerate(items_raw, start=1):
            item_entry = {
                "sequence": idx,
                "productOrService": {
                    "coding": [
                        {
                            "code": item.get("cpt_code"),
                        }
                    ]
                },
                "adjudication": [],
            }
            if item.get("charge"):
                item_entry["adjudication"].append(
                    {
                        "category": {"coding": [{"code": "submitted"}]},
                        "amount": {
                            "value": item["charge"],
                            "currency": item.get("currency", raw.get("currency", "USD")),
                        },
                    }
                )
            if item.get("allowed_amount"):
                item_entry["adjudication"].append(
                    {
                        "category": {"coding": [{"code": "allowed"}]},
                        "amount": {
                            "value": item["allowed_amount"],
                            "currency": item.get("currency", raw.get("currency", "USD")),
                        },
                    }
                )
            eob["item"].append(item_entry)

    return eob
