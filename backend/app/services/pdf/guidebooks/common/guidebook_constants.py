"""
TRADING TRUTH LAYER

GUIDEBOOK SERIES

CANONICAL SOURCE OF TRUTH FOR ALL
GUIDEBOOK-LEVEL CONSTANTS AND
INSTITUTIONAL PUBLICATION METADATA.

All guidebooks must consume their
institutional metadata from this module.

This module intentionally contains NO
PDF rendering logic and NO ReportLab
dependencies.

The purpose of this module is to ensure
that every volume speaks the same
institutional language throughout the
entire Trading Truth Layer ecosystem.
"""


# ==========================================================
# GUIDEBOOK SERIES METADATA
# ==========================================================

GUIDEBOOK_SERIES_NAME = "Trading Truth Layer Guidebook Series"

GUIDEBOOK_PUBLICATION_TYPE = "Institutional Publication Series"

GUIDEBOOK_VERSION = "Version 1.0"

GUIDEBOOK_SERIES_VERSION = "1.0"

GUIDEBOOK_AUTHOR = "Edward Emmanuely"

GUIDEBOOK_PUBLISHER = "Trading Truth Layer"

GUIDEBOOK_ORGANIZATION = "Trading Truth Layer"

GUIDEBOOK_WEBSITE = "www.tradingtruthlayer.com"

GUIDEBOOK_YEAR = "2026"

GUIDEBOOK_COPYRIGHT = (
    "Copyright © 2026 Trading Truth Layer. "
    "All rights reserved."
)


# ==========================================================
# TTL POSITIONING
# ==========================================================

TTL_POSITIONING_STATEMENT = (
    "Trading Truth Layer is Institutional Trading "
    "Trust Infrastructure for Evidence-Based "
    "Capital Allocation."
)

TTL_SHORT_POSITIONING_STATEMENT = (
    "Institutional Trading Trust Infrastructure "
    "for Evidence-Based Capital Allocation."
)

TTL_MISSION_STATEMENT = (
    "To establish the institutional trust "
    "infrastructure for global trading performance."
)

TTL_VISION_STATEMENT = (
    "To enable evidence-based capital allocation "
    "across global capital markets through "
    "institutional trust infrastructure."
)


# ==========================================================
# VOLUME TITLES
# ==========================================================

VOLUME_1_TITLE = (
    "The Foundations of Trading Trust Infrastructure"
)

VOLUME_2_TITLE = (
    "Institutional Trust Infrastructure Architecture"
)

VOLUME_3_TITLE = (
    "Trading Verification Infrastructure"
)

VOLUME_4_TITLE = (
    "Institutional Investigation Infrastructure"
)

VOLUME_5_TITLE = (
    "Capital Allocation Infrastructure"
)

VOLUME_6_TITLE = (
    "Public Trust Infrastructure"
)

VOLUME_7_TITLE = (
    "The Future of Trading Trust Infrastructure"
)


# ==========================================================
# VOLUME INSTITUTIONAL QUESTIONS
# ==========================================================

VOLUME_1_INSTITUTIONAL_QUESTION = (
    "Why does Trading Truth Layer exist?"
)

VOLUME_2_INSTITUTIONAL_QUESTION = (
    "How is Trading Truth Layer architected?"
)

VOLUME_3_INSTITUTIONAL_QUESTION = (
    "How does Trading Truth Layer verify trading performance?"
)

VOLUME_4_INSTITUTIONAL_QUESTION = (
    "How does Trading Truth Layer perform institutional investigations?"
)

VOLUME_5_INSTITUTIONAL_QUESTION = (
    "How does Trading Truth Layer determine institutional capital readiness?"
)

VOLUME_6_INSTITUTIONAL_QUESTION = (
    "How does Trading Truth Layer establish public trust?"
)

VOLUME_7_INSTITUTIONAL_QUESTION = (
    "What is the future of Trading Trust Infrastructure?"
)


# ==========================================================
# FOUR INSTITUTIONAL QUESTIONS
# ==========================================================

TTL_FOUR_QUESTIONS = [

    "Did the trading activity actually happen?",

    "Can the underlying evidence be independently trusted?",

    (
        "Can the performance record withstand "
        "institutional due diligence and "
        "verification procedures?"
    ),

    (
        "Can institutions confidently allocate "
        "capital based upon the presented "
        "trading record?"
    ),

]


# ==========================================================
# TTL DOCTRINE
# ==========================================================

TTL_DOCTRINE = [

    "Trading performance is institutional evidence.",

    "Institutional evidence requires institutional trust.",

    "Institutional trust requires institutional infrastructure.",

    (
        "Institutional infrastructure enables "
        "evidence-based capital allocation."
    ),

    (
        "Evidence-based capital allocation "
        "creates more efficient capital markets."
    ),

]


# ==========================================================
# CANONICAL INSTITUTIONAL STATEMENTS
# ==========================================================

TRUST_PROBLEM_STATEMENT = (
    "The trust problem is an infrastructure problem."
)

INSTITUTIONAL_TRUST_STATEMENT = (
    "Trust should not be optional."
)

INSTITUTIONAL_INFRASTRUCTURE_STATEMENT = (
    "Institutional trust should be infrastructure."
)

INSTITUTIONAL_EVIDENCE_STATEMENT = (
    "Trading performance is institutional evidence."
)

FUTURE_OF_TRUST_STATEMENT = (
    "The future of trading performance is trust."
)

FUTURE_OF_CAPITAL_ALLOCATION_STATEMENT = (
    "The future of capital allocation is evidence-based trust."
)

GLOBAL_CAPITAL_MARKETS_STATEMENT = (
    "Global capital allocation deserves institutional trust."
)

MISSING_INFRASTRUCTURE_STATEMENT = (
    "Global financial markets are missing institutional "
    "trading trust infrastructure."
)


# ==========================================================
# GUIDEBOOK DISCLAIMERS
# ==========================================================

GUIDEBOOK_DISCLAIMER = (
    "Trading Truth Layer Guidebooks are institutional "
    "publications designed to communicate the philosophical, "
    "architectural, and operational foundations of the "
    "Trading Truth Layer ecosystem."
)

INSTITUTIONAL_NOTICE = (
    "This publication is intended for educational and "
    "institutional purposes only and does not constitute "
    "investment advice, legal advice, or an offer to "
    "allocate capital."
)


# ==========================================================
# NEXT VOLUME METADATA
# ==========================================================

NEXT_VOLUME_METADATA = {

    1: {

        "next_volume": 2,

        "title": VOLUME_2_TITLE,

        "institutional_question": (
            VOLUME_2_INSTITUTIONAL_QUESTION
        ),

        "topics": [
            "Infrastructure Stack",
            "Core Engines",
            "Trust Layers",
            "Canonical Workflows",
            "Institutional Outputs",
            "Infrastructure Architecture",
        ],
    },

    2: {

        "next_volume": 3,

        "title": VOLUME_3_TITLE,

        "institutional_question": (
            VOLUME_3_INSTITUTIONAL_QUESTION
        ),

        "topics": [
            "Trading Verification Infrastructure",
            "Verification Metrics",
            "Verification Certificates",
            "Broker Synchronization",
            "Verification Workflows",
        ],
    },

    3: {

        "next_volume": 4,

        "title": VOLUME_4_TITLE,

        "institutional_question": (
            VOLUME_4_INSTITUTIONAL_QUESTION
        ),

        "topics": [
            "Institutional Investigations",
            "Investigation Engines",
            "Trust Intelligence",
            "Due Diligence Infrastructure",
        ],
    },

    4: {

        "next_volume": 5,

        "title": VOLUME_5_TITLE,

        "institutional_question": (
            VOLUME_5_INSTITUTIONAL_QUESTION
        ),

        "topics": [
            "Capital Allocation Infrastructure",
            "Allocator Workflows",
            "Trust Scores",
            "Institutional Readiness",
        ],
    },

    5: {

        "next_volume": 6,

        "title": VOLUME_6_TITLE,

        "institutional_question": (
            VOLUME_6_INSTITUTIONAL_QUESTION
        ),

        "topics": [
            "Public Trust Infrastructure",
            "Verification Networks",
            "Institutional Profiles",
            "Public Verification",
        ],
    },

    6: {

        "next_volume": 7,

        "title": VOLUME_7_TITLE,

        "institutional_question": (
            VOLUME_7_INSTITUTIONAL_QUESTION
        ),

        "topics": [
            "Trading Identity Infrastructure",
            "Global Trust Standards",
            "Future Institutional Markets",
            "The TTL Vision",
        ],
    },

}


# ==========================================================
# SECTION TITLES
# ==========================================================

PART_1_TITLE = "THE TRUST PROBLEM"

PART_2_TITLE = "THE MISSING INFRASTRUCTURE"

PART_3_TITLE = "TRADING TRUTH LAYER"

PART_4_TITLE = "THE TRADING TRUST INFRASTRUCTURE THESIS"

PART_5_TITLE = "THE TTL DOCTRINE"

PART_6_TITLE = "CONCLUSION"


# ==========================================================
# DOCUMENT TYPES
# ==========================================================

INSTITUTIONAL_WHITEPAPER = "Institutional Whitepaper"

INSTITUTIONAL_GUIDEBOOK = "Institutional Guidebook"

INSTITUTIONAL_PUBLICATION = "Institutional Publication"


# ==========================================================
# END OF FILE
# ==========================================================