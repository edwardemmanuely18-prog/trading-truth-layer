"""
Trading Truth Layer (TTL)

Financial Infrastructure Engine

MT760 Fields

Canonical MT760 field registry.

Defines every supported MT760 field together with
its business meaning and validation metadata.

The parser, validator and normalizer all consume this
registry instead of hardcoding field definitions.
"""

from __future__ import annotations

from dataclasses import dataclass

from typing import Dict


# ============================================================================
# Field Definition
# ============================================================================


@dataclass(frozen=True, slots=True)
class MT760Field:

    tag: str

    name: str

    sequence: str

    mandatory: bool

    description: str


# ============================================================================
# Sequence A
# General Information
# ============================================================================


SEQUENCE_A: Dict[str, MT760Field] = {

    "15A": MT760Field(
        tag="15A",
        name="New Sequence",
        sequence="A",
        mandatory=True,
        description="Start of Sequence A",
    ),

    "27": MT760Field(
        tag="27",
        name="Sequence of Total",
        sequence="A",
        mandatory=True,
        description="Message sequence information",
    ),

    "22A": MT760Field(
        tag="22A",
        name="Purpose of Message",
        sequence="A",
        mandatory=True,
        description="Purpose of the MT760 message",
    ),

    "72Z": MT760Field(
        tag="72Z",
        name="Sender to Receiver Information",
        sequence="A",
        mandatory=False,
        description="Additional sender instructions",
    ),

    "23X": MT760Field(
        tag="23X",
        name="File Identification",
        sequence="A",
        mandatory=False,
        description="File identification",
    ),
}


# ============================================================================
# Sequence B
# Undertaking Details
# ============================================================================


SEQUENCE_B: Dict[str, MT760Field] = {

    "15B": MT760Field(
        tag="15B",
        name="New Sequence",
        sequence="B",
        mandatory=True,
        description="Start of Sequence B",
    ),

    "20": MT760Field(
        tag="20",
        name="Undertaking Number",
        sequence="B",
        mandatory=True,
        description="Guarantee reference number",
    ),

    "30": MT760Field(
        tag="30",
        name="Date of Issue",
        sequence="B",
        mandatory=True,
        description="Issue date",
    ),

    "22D": MT760Field(
        tag="22D",
        name="Form of Undertaking",
        sequence="B",
        mandatory=True,
        description="Guarantee type",
    ),

    "40C": MT760Field(
        tag="40C",
        name="Applicable Rules",
        sequence="B",
        mandatory=True,
        description="Applicable guarantee rules",
    ),

    "23B": MT760Field(
        tag="23B",
        name="Expiry Type",
        sequence="B",
        mandatory=True,
        description="Expiry type",
    ),

    "31E": MT760Field(
        tag="31E",
        name="Expiry Date",
        sequence="B",
        mandatory=False,
        description="Guarantee expiry date",
    ),

    "35G": MT760Field(
        tag="35G",
        name="Expiry Event",
        sequence="B",
        mandatory=False,
        description="Expiry event",
    ),

    "50": MT760Field(
        tag="50",
        name="Applicant",
        sequence="B",
        mandatory=False,
        description="Applicant",
    ),

    "51": MT760Field(
        tag="51",
        name="Obligor",
        sequence="B",
        mandatory=False,
        description="Obligor / Instructing Party",
    ),

    "52A": MT760Field(
        tag="52A",
        name="Issuer",
        sequence="B",
        mandatory=True,
        description="Issuing institution (Option A)",
    ),

    "52D": MT760Field(
        tag="52D",
        name="Issuer",
        sequence="B",
        mandatory=True,
        description="Issuing institution (Option D)",
    ),

    "59": MT760Field(
        tag="59",
        name="Beneficiary",
        sequence="B",
        mandatory=True,
        description="Guarantee beneficiary",
    ),

    "32B": MT760Field(
        tag="32B",
        name="Undertaking Amount",
        sequence="B",
        mandatory=True,
        description="Guarantee amount",
    ),

    "71D": MT760Field(
        tag="71D",
        name="Charges",
        sequence="B",
        mandatory=False,
        description="Charges",
    ),

    "45C": MT760Field(
        tag="45C",
        name="Document Presentation Instructions",
        sequence="B",
        mandatory=False,
        description="Presentation conditions",
    ),
}


# ============================================================================
# Registry
# ============================================================================


MT760_FIELDS: Dict[str, MT760Field] = {}

MT760_FIELDS.update(SEQUENCE_A)

MT760_FIELDS.update(SEQUENCE_B)


MANDATORY_FIELDS = {

    tag

    for tag, field in MT760_FIELDS.items()

    if field.mandatory
}


OPTIONAL_FIELDS = {

    tag

    for tag, field in MT760_FIELDS.items()

    if not field.mandatory
}


# ============================================================================
# Public Exports
# ============================================================================


__all__ = [

    "MT760Field",

    "SEQUENCE_A",

    "SEQUENCE_B",

    "MT760_FIELDS",

    "MANDATORY_FIELDS",

    "OPTIONAL_FIELDS",
]