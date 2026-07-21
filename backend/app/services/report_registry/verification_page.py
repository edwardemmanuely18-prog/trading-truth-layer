from __future__ import annotations

from html import escape

from app.models.report_registry import ReportRegistry

import os


# ==========================================================
# Helpers
# ==========================================================

def _value(value) -> str:

    if value is None:
        return "Not Available"

    return escape(str(value))


def _status_badge(status: str) -> str:

    status = (status or "").upper()

    colors = {

        "DRAFT": "#6b7280",

        "VERIFIED": "#2563eb",

        "PUBLISHED": "#0891b2",

        "LOCKED": "#16a34a",

        "GENERATED": "#16a34a",

        "REGISTERED": "#16a34a",

        "REVOKED": "#dc2626",

        "ARCHIVED": "#7c3aed",

    }

    color = colors.get(

        status,

        "#334155",

    )

    return (
        f'<span class="badge-small" '
        f'style="background:{color};">'
        f'{escape(status.title())}'
        f'</span>'
    )


def _display_tier(value) -> str:

    if value is None:
        return "Not Available"

    mapping = {

        "tier_1": "Tier I",
        "tier_2": "Tier II",
        "tier_3": "Tier III",

        "TIER_1": "Tier I",
        "TIER_2": "Tier II",
        "TIER_3": "Tier III",
    }

    return mapping.get(

        str(value),

        str(value),

    )


def _display_score(value):

    if value is None:
        return "Not Available"

    try:

        return f"{float(value):.2f} / 100"

    except Exception:

        return escape(str(value))


# ==========================================================
# Public Builder
# ==========================================================

def build_verification_page(
    report: ReportRegistry,
) -> str:

    metadata = report.metadata_json or {}

    backend_url = (
        os.getenv(
            "PUBLIC_BACKEND_URL",
            "http://127.0.0.1:8001",
        )
    ).rstrip("/")

    download_url = (
        f"{backend_url}/report/"
        f"{report.report_id}/download"
    )

    classification = metadata.get(

        "classification",

        "Institutional Report",

    )

    report_type = str(
        report.report_type or ""
    ).upper()

    is_investigation_report = (

        report_type in {

            "INVESTIGATION",

            "EXECUTIVE",

        }

    )

    verification_status = metadata.get(
        "verification_status",
    )

    certificate_version = metadata.get(
        "certificate_version",
    )

    tvs_version = metadata.get(
        "tvs_version",
    )

    registry_state = metadata.get(

        "registry_state",

        "REGISTERED",

    )

    verification_score = metadata.get(

        "verification_score",

    )

    #
    # Allocator metrics
    #

    allocator_score = metadata.get(
        "allocator_score",
    )

    allocator_grade = metadata.get(
        "allocator_grade",
    )

    institutional_ready = metadata.get(
        "institutional_ready",
    )

    review_required = metadata.get(
        "review_required",
    )

    capital_allocation = metadata.get(
        "capital_allocation",
    )

    #
    # Investigation metadata
    #

    investigation_confidence = metadata.get(
        "investigation_confidence",
    )

    overall_risk = metadata.get(
        "overall_risk",
    )

    critical_findings = metadata.get(
        "critical_findings",
    )

    provider_count = metadata.get(
        "provider_count",
    )

    recommendations = metadata.get(
        "recommendations",
    )

    total_nodes = metadata.get(
        "total_nodes",
    )

    investigation_summary = metadata.get(
        "investigation_summary",
    )


    #
    # Portfolio metrics
    #

    verified_claims = metadata.get(
        "verified_claims",
    )

    verified_trades = metadata.get(
        "verified_trades",
    )

    average_verification_score = metadata.get(
        "average_verification_score",
    )

    highest_certificate = metadata.get(
        "highest_certificate",
    )

    lowest_certificate = metadata.get(
        "lowest_certificate",
    )

    median_certificate = metadata.get(
        "median_certificate",
    )


    #
    # TVS assessment
    #

    performance = metadata.get(
        "performance",
    )

    risk = metadata.get(
        "risk",
    )

    integrity = metadata.get(
        "integrity",
    )

    governance = metadata.get(
        "governance",
    )


    #
    # Governance metrics
    #

    transparency = metadata.get(
        "transparency",
    )

    network = metadata.get(
        "network",
    )

    reviews = metadata.get(
        "reviews",
    )

    disputes = metadata.get(
        "disputes",
    )

    stability = metadata.get(
        "stability",
    )

    generated = (

        report.generated_at.strftime(

            "%Y-%m-%d %H:%M UTC"

        )

        if report.generated_at

        else "Unknown"

    )

    metadata_rows = ""

    ignored = {

        #
        # Common metadata
        #

        "classification",
        "claim_status",
        "visibility",
        "registry_state",

        #
        # Verification metadata
        #

        "verification_status",
        "verification_band",
        "verification_tier",
        "primary_evidence",
        "evidence_source",
        "certificate_version",
        "tvs_version",

        #
        # Allocator metadata
        #

        "verification_score",
        "allocator_score",
        "allocator_grade",
        "institutional_ready",
        "review_required",
        "capital_allocation",

        "verified_claims",
        "verified_trades",

        "average_verification_score",
        "highest_certificate",
        "lowest_certificate",
        "median_certificate",

        "performance",
        "risk",
        "integrity",
        "governance",

        "transparency",
        "network",
        "reviews",
        "disputes",
        "stability",

    }

    for key, value in metadata.items():

        if key in {

            "verification_tier",

            "primary_evidence",

            "evidence_tier",

        }:

            value = _display_tier(value)

        elif key == "verification_status":

            value = str(value).title()

        elif key == "verification_score":

            value = _display_score(value)


        #
        # Investigation / Executive reports
        #

        if is_investigation_report:
            continue

            investigation_rows += f"""
            <tr>

            <th>
            {escape(str(key).replace("_"," ").title())}
            </th>

            <td>
            {escape(str(value))}
            </td>

            </tr>
            """

            continue

            investigation_rows += f"""

            <tr>

                <th>

                {escape(str(key).replace("_", " ").title())}

                </th>

                <td>

                {escape(str(value))}

                </td>

            </tr>

            """

            continue


        #
        # Existing logic
        #

        if key in ignored:

            continue


        metadata_rows += f"""

        <tr>

            <th>

            {escape(str(key).replace("_", " ").title())}

            </th>

            <td>

            {escape(str(value))}

            </td>

        </tr>

        """

    return f"""

<!DOCTYPE html>

<html lang="en">

<head>

<meta charset="utf-8">

<title>{_value(report.report_title)}</title>

<meta
name="viewport"
content="width=device-width, initial-scale=1">

<style>

* {{

    box-sizing:border-box;

}}

body {{

    margin:0;

    background:#eef2f7;

    font-family:
        Inter,
        ui-sans-serif,
        system-ui,
        -apple-system,
        BlinkMacSystemFont,
        "Segoe UI",
        sans-serif;

    color:#172033;

}}

.container {{

    width:980px;

    margin:40px auto;

    background:white;

    border-radius:14px;

    overflow:hidden;

    box-shadow:

        0 20px 45px rgba(15,23,42,.08);

}}

.header {{

    background:#0f172a;

    color:white;

    padding:42px;

}}

.header h1 {{

    margin:0;

    font-size:34px;

}}

.header p {{

    margin-top:12px;

    color:#cbd5e1;

}}

.badge {{

    display:inline-block;

    margin-top:20px;

    padding:10px 18px;

    background:#16a34a;

    border-radius:999px;

    color:white;

    font-size:13px;

    font-weight:bold;

    letter-spacing:.08em;

}}

.badge-small {{

    display:inline-block;

    color:white;

    padding:4px 10px;

    border-radius:999px;

    font-size:11px;

    line-height:1.2;

    font-weight:600;

    letter-spacing:.02em;

}}

.section {{

    padding:34px;

}}

.panel {{

    border:1px solid #dbe4ef;

    background:#f8fafc;

    border-radius:10px;

    padding:22px;

    margin-bottom:28px;

}}

.panel h3 {{

    margin:0 0 18px 0;

    color:#0f172a;

}}

.panel ul {{

    margin:0;

    padding-left:18px;

    line-height:2;

}}

table {{

    width:100%;

    border-collapse:collapse;

}}

th, td {{

    text-align:left;

    padding:13px;

    border-bottom:1px solid #edf2f7;

}}

th {{

    width:270px;

    color:#475569;

    font-weight:600;

}}

.download {{

    display:inline-block;

    margin-top:30px;

    background:#0f172a;

    color:white;

    text-decoration:none;

    padding:15px 28px;

    border-radius:8px;

    font-weight:bold;

}}

.footer {{

    padding:28px;

    text-align:center;

    background:#f8fafc;

    color:#64748b;

    font-size:13px;

    border-top:1px solid #e2e8f0;

}}

</style>

</head>

<body>

<div class="container">

<div class="header">

<h1>Trading Truth Layer</h1>

<p>

Institutional Report Registry

</p>

<div class="badge">

AUTHENTIC DOCUMENT

</div>

</div>

<div class="section">

<div class="panel">

<h3>

Document Authenticity

</h3>

<ul>

<li>

Registered in the Trading Truth Layer
Institutional Report Registry

</li>

<li>

SHA-256 Fingerprint Verified

</li>

<li>

Immutable Institutional Artifact

</li>

<li>

Canonical Report Identifier Assigned

</li>

<li>

Registry Status:
{_status_badge(registry_state)}

</li>

<li>

Verification Status:
{
    _status_badge(verification_status)
    if verification_status
    else "Not Available"
}

</li>


</ul>

</div>

<h2 style="margin-bottom:8px;">

{_value(report.report_title)}

</h2>

<p
style="
margin-top:0;
margin-bottom:28px;
color:#64748b;
font-size:15px;
">

Classification

<strong>

{_value(classification)}

</strong>

</p>

<table>

<tr>

<th>

Report ID

</th>

<td>

{_value(report.report_id)}

</td>

</tr>

<tr>

<th>

Report Type

</th>

<td>

{_value(report.report_type)}

</td>

</tr>

<tr>

<th>

Registry Status

</th>

<td>

{_status_badge(report.status)}

</td>

</tr>

</tr>

<th>

Verification Status

</th>

<td>

{
    _status_badge(verification_status)
    if verification_status
    else "Not Available"
}

</td>

<tr>

<th>

Certificate Version

</th>

<td>

{_value(certificate_version)}

</td>

</tr>

<tr>

<th>

TVS Version

</th>

<td>

{_value(tvs_version)}

</td>

</tr>

<tr>

<th>

Workspace

</th>

<td>

{report.workspace_id}

</td>

</tr>

<tr>

<th>

Generated

</th>

<td>

{generated}

</td>

</tr>

<tr>

<th>

SHA-256 Fingerprint

</th>

<td
style="
word-break:break-all;
font-family:monospace;
">

{_value(report.sha256)}

</td>

</tr>

<tr>

<th>

File Size

</th>

<td>

{report.file_size:,} bytes

</td>

</tr>

{

f'''

<tr>

<th>

Verification Score

</th>

<td>

{verification_score:.1f} / 100

</td>

</tr>

'''

if isinstance(
    verification_score,
    (int, float),
)

else ""

}

</table>

{
f"""

<h3 style="margin-top:42px;">

Institutional Investigation Metadata

</h3>

<table>

<tr>
<th>Scope</th>
<td>{_value(metadata.get("scope"))}</td>
</tr>

<tr>
<th>Total Nodes</th>
<td>{_value(total_nodes)}</td>
</tr>

<tr>
<th>Overall Risk</th>
<td>{_value(overall_risk)}</td>
</tr>

<tr>
<th>Provider Count</th>
<td>{_value(provider_count)}</td>
</tr>

<tr>
<th>Recommendations</th>
<td>{_value(recommendations)}</td>
</tr>

<tr>
<th>Critical Findings</th>
<td>{_value(critical_findings)}</td>
</tr>

<tr>
<th>Investigation Confidence</th>
<td>{_display_score(investigation_confidence)}</td>
</tr>

</table>

"""
if is_investigation_report

else

f"""

<h3
style="
margin-top:42px;
">

Verification Metadata

</h3>

<table>

{metadata_rows}

</table>

"""

}

{
f"""

<h3 style="margin-top:42px;">

Institutional Conclusion

</h3>

<div class="panel">

<p style="margin:0; line-height:1.8;">

{_value(investigation_summary)}

</p>

</div>

"""

if (
    is_investigation_report
    and investigation_summary
)
else ""
}

<a
    class="download"
    href="{download_url}"
    target="_blank"
    rel="noopener noreferrer"
>
    Download Registered PDF
</a>

</div>

<div class="footer">

<div
style="
font-weight:bold;
margin-bottom:12px;
color:#0f172a;
">

Trading Truth Layer

Institutional Report Registry

</div>

This document is an immutable institutional
artifact registered within the Trading Truth
Layer Report Registry.

<br><br>

Any modification to this PDF changes its
SHA-256 fingerprint and invalidates registry
verification.

<br><br>

Registry Status:
<strong>{_value(registry_state)}</strong>

&nbsp;&nbsp;|&nbsp;&nbsp;

Verification:
<strong>{str(verification_status).title()}</strong>

Version:
<strong>{_value(certificate_version)}</strong>

&nbsp;&nbsp;|&nbsp;&nbsp;

TVS:
<strong>{_value(tvs_version)}</strong>

&nbsp;&nbsp;|&nbsp;&nbsp;

Report ID:
<strong>

{_value(report.report_id)}

</strong>

</div>

</div>

</body>

</html>

"""