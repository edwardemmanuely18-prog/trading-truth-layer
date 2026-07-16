from __future__ import annotations

from typing import Any

from reportlab.platypus import KeepTogether

from reportlab.platypus import (
    Spacer,
)

from reportlab.platypus import (
    Spacer,
    PageBreak,
)

from app.services.investigations.models import (
    InvestigationDomain,
    InvestigationReport,
)

from app.services.pdf.common.institutional_sections import (
    build_narrative,
    build_section_title,
)

from app.services.pdf.common.institutional_tables import (
    build_key_value_table,
)


# ==========================================================
# Helpers
# ==========================================================


def _confidence(domain: InvestigationDomain | None) -> str:
    if not domain:
        return "Not Available"

    return f"{domain.confidence:.2f}%"


def _status(domain: InvestigationDomain | None) -> str:
    return "Completed" if domain else "Not Executed"


def _finding_count(domain: InvestigationDomain | None) -> str:
    if not domain:
        return "0"

    return str(len(domain.findings))


def _metadata_lines(domain: InvestigationDomain | None) -> list[str]:

    if not domain:
        return []

    metadata = domain.metadata or {}

    lines: list[str] = []

    for key, value in metadata.items():

        if value in (
            None,
            "",
            [],
            {},
            "Unknown",
        ):
            continue

        label = key.replace("_", " ").title()

        lines.append(
            f"{label}: {value}"
        )

    return lines


# ==========================================================
# Domain Card
# ==========================================================


def _build_domain_card(
    story: list[Any],
    title: str,
    domain: InvestigationDomain | None,
) -> None:

    #
    # Keep ONLY the summary together.
    #

    story.append(

        KeepTogether(

            [

                build_key_value_table(

                    {

                        "Domain": title,

                        "Status": _status(domain),

                        "Confidence": _confidence(domain),

                        "Findings": _finding_count(domain),

                    }

                )

            ]

        )

    )

    metadata = _metadata_lines(domain)

    if metadata:

        details = {}

        for line in metadata:

            if ":" not in line:
                continue

            key, value = line.split(":", 1)

            details[key.strip()] = value.strip()

        story.extend(

            build_narrative(

                [

                    "Key Investigation Details",

                ]

            )

        )

        #
        # DO NOT wrap this large table in KeepTogether.
        #

        story.append(

            build_key_value_table(details)

        )

    else:

        story.extend(

            build_narrative(

                [

                    "No additional investigation details were produced for this analytical domain."

                ]

            )

        )


# ==========================================================
# Domain Investigation
# ==========================================================


def build_investigation_domains(
    story: list[Any],
    report: InvestigationReport,
) -> None:

    story.extend(

        build_section_title(

            "Institutional Domain Investigation",

        )

    )

    story.extend(

        build_narrative(

            [

                (
                    "The Institutional Investigation System evaluates "
                    "eight independent analytical domains before the "
                    "allocator produces its final institutional decision."
                ),

                (
                    "Each domain preserves its own evidence, findings "
                    "and confidence score while remaining fully "
                    "traceable to the canonical Investigation Context."
                ),

            ]

        )

    )

    story.append(
        Spacer(
            1,
            8,
        )
    )

    domains = [

        ("Execution Analysis", report.execution),

        ("Evidence Analysis", report.evidence),

        ("Verification Analysis", report.verification),

        ("Governance Analysis", report.governance),

        ("Broker Analysis", report.broker),

        ("Synchronization Analysis", report.synchronization),

        ("Review Analysis", report.review),

        ("Behaviour Analysis", report.behavior),

    ]

    for index, (title, domain) in enumerate(domains):

        if index:

            story.append(
                Spacer(
                    1,
                    8,
                )
            )

        _build_domain_card(
            story,
            title,
            domain,
        )

    story.extend(

        build_narrative(

            [

                (
                    "Together these analytical domains provide the "
                    "institutional evidence base used by the allocator "
                    "to produce a transparent, reproducible and "
                    "independently verifiable investigation outcome."
                )

            ]

        )

    )

    story.append(
        Spacer(
            1,
            18,
        )
    )