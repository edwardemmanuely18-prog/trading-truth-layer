"""
Trading Truth Layer

Volume IV

Institutional Capital Allocation Infrastructure

Domain VII

Public Trust Layer
"""

from reportlab.platypus import (
    Paragraph,
    Spacer,
    PageBreak,
)

from app.services.pdf.common.institutional_theme import (
    TITLE_STYLE,
    SUBTITLE_STYLE,
    BODY_STYLE,
    BODY_CENTER_STYLE,
    SPACE_MD,
    SPACE_LG,
)


# ==========================================================
# PUBLIC API
# ==========================================================


def build_domain_7_public_trust_layer():

    """
    Builds Domain VII.

    Public Trust Layer.
    """

    story = []

    # --------------------------------------------------
    # DOMAIN TITLE
    # --------------------------------------------------

    story.append(
        Paragraph(
            "DOMAIN VII",
            TITLE_STYLE,
        )
    )

    story.append(
        Spacer(
            1,
            SPACE_MD,
        )
    )

    story.append(
        Paragraph(
            "PUBLIC TRUST LAYER",
            SUBTITLE_STYLE,
        )
    )

    story.append(
        Paragraph(
            "(PUBLIC TRUST INFRASTRUCTURE)",
            BODY_CENTER_STYLE,
        )
    )

    story.append(
        Spacer(
            1,
            SPACE_LG,
        )
    )

    # --------------------------------------------------
    # WHAT IS THE INFRASTRUCTURE?
    # --------------------------------------------------

    story.append(
        Paragraph(
            "WHAT IS THE INFRASTRUCTURE?",
            SUBTITLE_STYLE,
        )
    )

    story.append(
        Spacer(
            1,
            SPACE_MD,
        )
    )

    story.append(
        Paragraph(
            "The Public Trust Layer represents the public-facing "
            "trust infrastructure of the Trading Truth Layer.",
            BODY_STYLE,
        )
    )

    story.append(
        Paragraph(
            "It is responsible for transforming institutionally "
            "verified trading claims into publicly discoverable, "
            "externally verifiable and allocator-accessible trust "
            "records.",
            BODY_STYLE,
        )
    )

    story.append(
        Paragraph(
            "While the institutional trust pipeline governs "
            "verification, evidence evaluation and allocator "
            "intelligence internally, the Public Trust Layer "
            "governs how institutionally verified claims are "
            "exposed to the outside world.",
            BODY_STYLE,
        )
    )

    story.append(
        Paragraph(
            "The Public Trust Layer provides the infrastructure "
            "required for allocators, investors, auditors, family "
            "offices, hedge funds, proprietary trading firms and "
            "other institutional participants to independently "
            "discover, verify and assess publicly exposed trading "
            "records.",
            BODY_STYLE,
        )
    )

    story.append(
        Spacer(
            1,
            SPACE_LG,
        )
    )

    # --------------------------------------------------
    # PRIMARY RESPONSIBILITIES
    # --------------------------------------------------

    story.append(
        Paragraph(
            "PRIMARY RESPONSIBILITIES",
            SUBTITLE_STYLE,
        )
    )

    story.append(
        Spacer(
            1,
            SPACE_MD,
        )
    )

    responsibilities = [

        "Public claim publication.",

        "Canonical verification route management.",

        "Public trust record discovery.",

        "Institutional verification intelligence.",

        "Verification network monitoring.",

        "Public visibility management.",

        "Allocator accessibility.",

        "Governance-ready trust exposure.",

        "External trust distribution.",

        "Institutional publication readiness.",

    ]

    for responsibility in responsibilities:

        story.append(
            Paragraph(
                f"• {responsibility}",
                BODY_STYLE,
            )
        )

    story.append(
        Spacer(
            1,
            SPACE_LG,
        )
    )

    # --------------------------------------------------
    # INSTITUTIONAL SUBDOMAINS
    # --------------------------------------------------

    story.append(
        Paragraph(
            "INSTITUTIONAL SUBDOMAINS",
            SUBTITLE_STYLE,
        )
    )

    story.append(
        Spacer(
            1,
            SPACE_MD,
        )
    )

    subdomains = [

        "Public Records.",

        "Verification Routes.",

        "Trust Directory.",

        "Verification Network.",

        "External Reviews.",

        "Evidence Graph.",

        "Public Profiles.",

    ]

    for subdomain in subdomains:

        story.append(
            Paragraph(
                f"• {subdomain}",
                BODY_STYLE,
            )
        )

    story.append(
        Paragraph(
            "Collectively, these institutional trust surfaces "
            "constitute the Public Trust Infrastructure of the "
            "Trading Truth Layer.",
            BODY_STYLE,
        )
    )

    story.append(
        Spacer(
            1,
            SPACE_LG,
        )
    )

    # --------------------------------------------------
    # INSTITUTIONAL PURPOSE
    # --------------------------------------------------

    story.append(
        Paragraph(
            "INSTITUTIONAL PURPOSE",
            SUBTITLE_STYLE,
        )
    )

    story.append(
        Spacer(
            1,
            SPACE_MD,
        )
    )

    story.append(
        Paragraph(
            "The Public Trust Layer enables institutionally "
            "verified trading records to become discoverable, "
            "externally verifiable and institutionally accessible "
            "without compromising the integrity and governance "
            "standards established by the institutional "
            "verification pipeline.",
            BODY_STYLE,
        )
    )

    story.append(
        Spacer(
            1,
            SPACE_LG,
        )
    )

    # --------------------------------------------------
    # PUBLIC RECORDS
    # --------------------------------------------------

    story.append(
        Paragraph(
            "PUBLIC RECORDS",
            SUBTITLE_STYLE,
        )
    )

    story.append(
        Spacer(
            1,
            SPACE_MD,
        )
    )

    story.append(
        Paragraph(
            "The Public Records page serves as the institutional "
            "publication layer of the Trading Truth Layer.",
            BODY_STYLE,
        )
    )

    story.append(
        Paragraph(
            "Every publicly exposed claim within the workspace is "
            "registered together with its lifecycle status, trust "
            "posture and public verification metadata.",
            BODY_STYLE,
        )
    )

    story.append(
        Paragraph(
            "The Public Records page enables workspace owners, "
            "allocators and external reviewers to determine which "
            "claims have successfully progressed through the "
            "institutional verification pipeline and are available "
            "for public trust evaluation.",
            BODY_STYLE,
        )
    )

    story.append(
        Spacer(
            1,
            SPACE_LG,
        )
    )

    # --------------------------------------------------
    # PUBLIC RECORDS CAPABILITIES
    # --------------------------------------------------

    story.append(PageBreak())

    story.append(
        Paragraph(
            "PUBLIC RECORDS CAPABILITIES",
            SUBTITLE_STYLE,
        )
    )

    story.append(
        Spacer(
            1,
            SPACE_MD,
        )
    )

    public_records_capabilities = [

        "Public claim registry.",

        "Verification posture.",

        "Trust score exposure.",

        "Integrity status monitoring.",

        "Claim lifecycle information.",

        "Publication timestamps.",

        "Public visibility controls.",

        "Claim hashes and canonical identifiers.",

        "Verification route access.",

        "External review submission access.",

    ]

    for capability in public_records_capabilities:

        story.append(
            Paragraph(
                f"• {capability}",
                BODY_STYLE,
            )
        )

    story.append(
        Spacer(
            1,
            SPACE_LG,
        )
    )

    # --------------------------------------------------
    # PUBLIC CLAIM RECORDS
    # --------------------------------------------------

    story.append(
        Paragraph(
            "PUBLIC CLAIM RECORDS",
            SUBTITLE_STYLE,
        )
    )

    story.append(
        Spacer(
            1,
            SPACE_MD,
        )
    )

    public_claim_records = [

        "Claim identifier.",

        "Trade statistics.",

        "Trust intelligence metrics.",

        "Publication metadata.",

        "Integrity monitoring status.",

        "Verification timestamps.",

        "Public visibility information.",

        "Canonical claim hash.",

        "Verification route access.",

        "External review capabilities.",

    ]

    for record in public_claim_records:

        story.append(
            Paragraph(
                f"• {record}",
                BODY_STYLE,
            )
        )

    story.append(
        Paragraph(
            "The Public Records page acts as the canonical registry "
            "of publicly exposed claims and represents the first "
            "layer of institutional trust publication within the "
            "workspace.",
            BODY_STYLE,
        )
    )

    story.append(
        Spacer(
            1,
            SPACE_LG,
        )
    )

        # --------------------------------------------------
    # VERIFICATION ROUTES
    # --------------------------------------------------

    story.append(PageBreak())

    story.append(
        Paragraph(
            "VERIFICATION ROUTES",
            SUBTITLE_STYLE,
        )
    )

    story.append(
        Spacer(
            1,
            SPACE_MD,
        )
    )

    story.append(
        Paragraph(
            "The Verification Routes page provides the canonical "
            "verification endpoints for externally verifiable "
            "claims published through the Trading Truth Layer.",
            BODY_STYLE,
        )
    )

    story.append(
        Paragraph(
            "Every publicly exposed claim receives its own "
            "cryptographically addressable verification route, "
            "enabling allocators, investors, auditors and external "
            "reviewers to independently verify institutional "
            "trading records.",
            BODY_STYLE,
        )
    )

    story.append(
        Paragraph(
            "Verification Routes establish the public verification "
            "infrastructure required for institutional trust "
            "distribution across global capital markets.",
            BODY_STYLE,
        )
    )

    story.append(
        Spacer(
            1,
            SPACE_LG,
        )
    )

    # --------------------------------------------------
    # VERIFICATION ROUTE CAPABILITIES
    # --------------------------------------------------

    story.append(
        Paragraph(
            "VERIFICATION ROUTE CAPABILITIES",
            SUBTITLE_STYLE,
        )
    )

    story.append(
        Spacer(
            1,
            SPACE_MD,
        )
    )

    route_capabilities = [

        "Canonical verification endpoints.",

        "Public verification routes.",

        "Claim publication routes.",

        "Verification coverage metrics.",

        "Claim lifecycle exposure.",

        "Public verification timestamps.",

        "Locked record monitoring.",

        "Public route readiness indicators.",

        "Verification route registry.",

    ]

    for capability in route_capabilities:

        story.append(
            Paragraph(
                f"• {capability}",
                BODY_STYLE,
            )
        )

    story.append(
        Spacer(
            1,
            SPACE_LG,
        )
    )

    # --------------------------------------------------
    # VERIFICATION ROUTE METADATA
    # --------------------------------------------------

    story.append(
        Paragraph(
            "VERIFICATION ROUTE METADATA",
            SUBTITLE_STYLE,
        )
    )

    story.append(
        Spacer(
            1,
            SPACE_MD,
        )
    )

    verification_route_metadata = [

        "Canonical claim hash.",

        "Verification endpoint.",

        "Public claim route.",

        "Verification timestamp.",

        "Publication timestamp.",

        "Lock timestamp.",

        "Public route status.",

        "Verification readiness status.",

    ]

    for item in verification_route_metadata:

        story.append(
            Paragraph(
                f"• {item}",
                BODY_STYLE,
            )
        )

    story.append(
        Paragraph(
            "The Verification Routes page establishes the public "
            "verification infrastructure of the Trading Truth "
            "Layer by enabling every published claim to become "
            "externally verifiable through canonical trust "
            "endpoints.",
            BODY_STYLE,
        )
    )

    story.append(
        Spacer(
            1,
            SPACE_LG,
        )
    )

    # --------------------------------------------------
    # TRUST DIRECTORY
    # --------------------------------------------------

    story.append(
        Paragraph(
            "TRUST DIRECTORY",
            SUBTITLE_STYLE,
        )
    )

    story.append(
        Spacer(
            1,
            SPACE_MD,
        )
    )

    story.append(
        Paragraph(
            "The Trust Directory acts as the institutional "
            "discovery layer of the Public Trust Layer.",
            BODY_STYLE,
        )
    )

    story.append(
        Paragraph(
            "It aggregates publicly exposed claims, verification "
            "routes and trust-ready entities into a single "
            "discoverable institutional registry.",
            BODY_STYLE,
        )
    )

    story.append(
        Paragraph(
            "The Trust Directory is designed to provide allocators "
            "and external institutions with a centralized location "
            "for discovering publicly accessible trading records "
            "and their associated verification infrastructure.",
            BODY_STYLE,
        )
    )

    story.append(
        Spacer(
            1,
            SPACE_LG,
        )
    )

    # --------------------------------------------------
    # TRUST DIRECTORY CAPABILITIES
    # --------------------------------------------------

    story.append(
        Paragraph(
            "TRUST DIRECTORY CAPABILITIES",
            SUBTITLE_STYLE,
        )
    )

    story.append(
        Spacer(
            1,
            SPACE_MD,
        )
    )

    trust_directory_capabilities = [

        "Public trust record discovery.",

        "Verification route discovery.",

        "Governance-ready claim exposure.",

        "Publication status monitoring.",

        "Locked record registry.",

        "Public visibility management.",

        "Verification readiness indicators.",

        "Public trust search capabilities.",

    ]

    for capability in trust_directory_capabilities:

        story.append(
            Paragraph(
                f"• {capability}",
                BODY_STYLE,
            )
        )

    story.append(
        Spacer(
            1,
            SPACE_LG,
        )
    )

    # --------------------------------------------------
    # TRUST DIRECTORY METADATA
    # --------------------------------------------------

    story.append(
        Paragraph(
            "TRUST DIRECTORY METADATA",
            SUBTITLE_STYLE,
        )
    )

    story.append(
        Spacer(
            1,
            SPACE_MD,
        )
    )

    trust_directory_metadata = [

        "Claim identifier.",

        "Verification status.",

        "Publication status.",

        "Lock status.",

        "Public record route.",

        "Verification route.",

        "Publication timestamps.",

        "Verification timestamps.",

        "Visibility posture.",

        "Institutional readiness information.",

    ]

    for item in trust_directory_metadata:

        story.append(
            Paragraph(
                f"• {item}",
                BODY_STYLE,
            )
        )

    story.append(
        Paragraph(
            "The Trust Directory functions as the discoverability "
            "engine of the Public Trust Layer by exposing publicly "
            "verifiable trust records in an allocator-friendly "
            "institutional registry.",
            BODY_STYLE,
        )
    )

    story.append(
        Spacer(
            1,
            SPACE_LG,
        )
    )

        # --------------------------------------------------
    # VERIFICATION NETWORK
    # --------------------------------------------------

    story.append(
        Paragraph(
            "VERIFICATION NETWORK",
            SUBTITLE_STYLE,
        )
    )

    story.append(
        Spacer(
            1,
            SPACE_MD,
        )
    )

    story.append(
        Paragraph(
            "The Verification Network page provides executive-level "
            "trust intelligence regarding the institutional health "
            "of the workspace's public verification infrastructure.",
            BODY_STYLE,
        )
    )

    story.append(
        Paragraph(
            "It aggregates publication readiness, verification "
            "coverage, broker connectivity, governance health, "
            "integrity monitoring and public exposure metrics into "
            "a single institutional trust intelligence surface.",
            BODY_STYLE,
        )
    )

    story.append(
        Paragraph(
            "The Verification Network represents the executive "
            "trust intelligence layer of the Public Trust Layer.",
            BODY_STYLE,
        )
    )

    story.append(
        Spacer(
            1,
            SPACE_LG,
        )
    )

    # --------------------------------------------------
    # VERIFICATION NETWORK CAPABILITIES
    # --------------------------------------------------

    story.append(
        Paragraph(
            "VERIFICATION NETWORK CAPABILITIES",
            SUBTITLE_STYLE,
        )
    )

    story.append(
        Spacer(
            1,
            SPACE_MD,
        )
    )

    network_capabilities = [

        "Institutional trust score.",

        "Verification coverage intelligence.",

        "Publication readiness metrics.",

        "Governance health monitoring.",

        "Broker verification intelligence.",

        "Claim lifecycle monitoring.",

        "Integrity monitoring metrics.",

        "Public visibility exposure.",

        "Institutional registry information.",

        "Allocator readiness indicators.",

    ]

    for capability in network_capabilities:

        story.append(
            Paragraph(
                f"• {capability}",
                BODY_STYLE,
            )
        )

    story.append(
        Spacer(
            1,
            SPACE_LG,
        )
    )

    # --------------------------------------------------
    # INSTITUTIONAL VERIFICATION INTELLIGENCE
    # --------------------------------------------------

    story.append(PageBreak())

    story.append(
        Paragraph(
            "INSTITUTIONAL VERIFICATION INTELLIGENCE",
            SUBTITLE_STYLE,
        )
    )

    story.append(
        Spacer(
            1,
            SPACE_MD,
        )
    )

    story.append(
        Paragraph(
            "Institutional Verification Intelligence provides "
            "executive trust metrics describing the public trust "
            "health of the workspace.",
            BODY_STYLE,
        )
    )

    verification_intelligence = [

        "Workspace trust score.",

        "Network health.",

        "Verification band.",

        "Verification coverage.",

        "Allocator readiness status.",

    ]

    for intelligence in verification_intelligence:

        story.append(
            Paragraph(
                f"• {intelligence}",
                BODY_STYLE,
            )
        )

    story.append(
        Spacer(
            1,
            SPACE_LG,
        )
    )

    # --------------------------------------------------
    # VERIFICATION COVERAGE METRICS
    # --------------------------------------------------

    story.append(
        Paragraph(
            "VERIFICATION COVERAGE METRICS",
            SUBTITLE_STYLE,
        )
    )

    story.append(
        Spacer(
            1,
            SPACE_MD,
        )
    )

    story.append(
        Paragraph(
            "Verification Coverage Metrics provide institutional "
            "publication intelligence across all publicly exposed "
            "claims contained within the workspace.",
            BODY_STYLE,
        )
    )

    coverage_metrics = [

        "Verification coverage.",

        "Publication coverage.",

        "Lock coverage.",

    ]

    for metric in coverage_metrics:

        story.append(
            Paragraph(
                f"• {metric}",
                BODY_STYLE,
            )
        )

    story.append(
        Paragraph(
            "These metrics communicate the maturity of the public "
            "trust publication pipeline.",
            BODY_STYLE,
        )
    )

    story.append(
        Spacer(
            1,
            SPACE_LG,
        )
    )

    # --------------------------------------------------
    # CLAIM VERIFICATION PIPELINE
    # --------------------------------------------------

    story.append(
        Paragraph(
            "CLAIM VERIFICATION PIPELINE",
            SUBTITLE_STYLE,
        )
    )

    story.append(
        Spacer(
            1,
            SPACE_MD,
        )
    )

    story.append(
        Paragraph(
            "The Claim Verification Pipeline provides lifecycle "
            "intelligence for all institutional claims operating "
            "inside the workspace.",
            BODY_STYLE,
        )
    )

    claim_pipeline = [

        "Draft claims.",

        "Verified claims.",

        "Published claims.",

        "Locked claims.",

        "Allocator readiness conditions.",

    ]

    for item in claim_pipeline:

        story.append(
            Paragraph(
                f"• {item}",
                BODY_STYLE,
            )
        )

    story.append(
        Paragraph(
            "The pipeline communicates the publication readiness "
            "status of the institutional trust infrastructure.",
            BODY_STYLE,
        )
    )

    story.append(
        Spacer(
            1,
            SPACE_LG,
        )
    )

        # --------------------------------------------------
    # BROKER VERIFICATION NETWORK
    # --------------------------------------------------

    story.append(PageBreak())

    story.append(
        Paragraph(
            "BROKER VERIFICATION NETWORK",
            SUBTITLE_STYLE,
        )
    )

    story.append(
        Spacer(
            1,
            SPACE_MD,
        )
    )

    story.append(
        Paragraph(
            "The Broker Verification Network provides institutional "
            "broker infrastructure intelligence across the public "
            "verification ecosystem.",
            BODY_STYLE,
        )
    )

    story.append(
        Paragraph(
            "Broker intelligence metrics assist allocators and "
            "institutional participants in assessing the maturity "
            "and diversity of broker connectivity capabilities "
            "supporting publicly verifiable claims.",
            BODY_STYLE,
        )
    )

    broker_metrics = [

        "Connected broker accounts.",

        "Verified broker accounts.",

        "Live account monitoring.",

        "Connected providers.",

        "Provider diversity metrics.",

    ]

    for metric in broker_metrics:

        story.append(
            Paragraph(
                f"• {metric}",
                BODY_STYLE,
            )
        )

    story.append(
        Spacer(
            1,
            SPACE_LG,
        )
    )

    # --------------------------------------------------
    # INTEGRITY MONITORING
    # --------------------------------------------------

    story.append(
        Paragraph(
            "INTEGRITY MONITORING",
            SUBTITLE_STYLE,
        )
    )

    story.append(
        Spacer(
            1,
            SPACE_MD,
        )
    )

    story.append(
        Paragraph(
            "Integrity Monitoring provides governance and "
            "operational intelligence regarding the institutional "
            "health of publicly exposed trust records.",
            BODY_STYLE,
        )
    )

    story.append(
        Paragraph(
            "Integrity intelligence enables institutions to "
            "evaluate whether publicly accessible claims continue "
            "to satisfy the governance standards established "
            "throughout the institutional verification pipeline.",
            BODY_STYLE,
        )
    )

    integrity_metrics = [

        "Integrity score.",

        "Open findings.",

        "Resolved findings.",

        "Claims scanned.",

        "Governance health monitoring.",

    ]

    for metric in integrity_metrics:

        story.append(
            Paragraph(
                f"• {metric}",
                BODY_STYLE,
            )
        )

    story.append(
        Spacer(
            1,
            SPACE_LG,
        )
    )

    # --------------------------------------------------
    # VERIFICATION NETWORK EXPOSURE
    # --------------------------------------------------

    story.append(
        Paragraph(
            "VERIFICATION NETWORK EXPOSURE",
            SUBTITLE_STYLE,
        )
    )

    story.append(
        Spacer(
            1,
            SPACE_MD,
        )
    )

    story.append(
        Paragraph(
            "Verification Network Exposure provides institutional "
            "visibility into the public trust posture of all "
            "claims participating within the publication "
            "infrastructure.",
            BODY_STYLE,
        )
    )

    exposure_metrics = [

        "Public claims.",

        "Private claims.",

        "Unlisted claims.",

        "Public visibility percentage.",

        "Verification route exposure.",

        "Public claim page availability.",

        "Allocator discovery status.",

        "Institutional visibility status.",

    ]

    for metric in exposure_metrics:

        story.append(
            Paragraph(
                f"• {metric}",
                BODY_STYLE,
            )
        )

    story.append(
        Paragraph(
            "These exposure metrics communicate the maturity of "
            "the public trust distribution infrastructure across "
            "the workspace.",
            BODY_STYLE,
        )
    )

    story.append(
        Spacer(
            1,
            SPACE_LG,
        )
    )

    # --------------------------------------------------
    # VERIFIED CLAIM REGISTRY
    # --------------------------------------------------

    story.append(
        Paragraph(
            "VERIFIED CLAIM REGISTRY",
            SUBTITLE_STYLE,
        )
    )

    story.append(
        Spacer(
            1,
            SPACE_MD,
        )
    )

    story.append(
        Paragraph(
            "The Verified Claim Registry provides institutional "
            "registry intelligence across all publicly verifiable "
            "claims operating inside the workspace.",
            BODY_STYLE,
        )
    )

    verified_claim_registry = [

        "Verified claim listing.",

        "Claim status monitoring.",

        "Visibility status.",

        "Network readiness status.",

        "Claim hashes.",

        "Verification actions.",

        "Public publication actions.",

    ]

    for item in verified_claim_registry:

        story.append(
            Paragraph(
                f"• {item}",
                BODY_STYLE,
            )
        )

    story.append(
        Paragraph(
            "The Verified Claim Registry acts as the canonical "
            "institutional registry of publicly verifiable trading "
            "claims participating in the Public Trust Layer.",
            BODY_STYLE,
        )
    )

    story.append(
        Spacer(
            1,
            SPACE_LG,
        )
    )

        # --------------------------------------------------
    # EXTERNAL REVIEWS
    # --------------------------------------------------

    story.append(
        Paragraph(
            "EXTERNAL REVIEWS",
            SUBTITLE_STYLE,
        )
    )

    story.append(
        Spacer(
            1,
            SPACE_MD,
        )
    )

    story.append(
        Paragraph(
            "The External Reviews domain provides the institutional "
            "review infrastructure of the Public Trust Layer.",
            BODY_STYLE,
        )
    )

    story.append(
        Paragraph(
            "It enables independent third-party participants to "
            "contribute governance observations, verification "
            "findings and due diligence intelligence surrounding "
            "publicly verifiable trading claims.",
            BODY_STYLE,
        )
    )

    story.append(
        Paragraph(
            "External reviews become part of the canonical trust "
            "context of a public claim and provide allocators, "
            "auditors, governance specialists and verification "
            "participants with additional institutional insight "
            "beyond the underlying performance record.",
            BODY_STYLE,
        )
    )

    story.append(
        Paragraph(
            "The External Reviews domain operates as a public trust "
            "augmentation layer that supports institutional capital "
            "allocation decisions and public verification processes.",
            BODY_STYLE,
        )
    )

    story.append(
        Spacer(
            1,
            SPACE_LG,
        )
    )

    # --------------------------------------------------
    # PRIMARY RESPONSIBILITIES
    # --------------------------------------------------

    story.append(
        Paragraph(
            "PRIMARY RESPONSIBILITIES",
            SUBTITLE_STYLE,
        )
    )

    story.append(
        Spacer(
            1,
            SPACE_MD,
        )
    )

    responsibilities = [

        "Institutional review submissions.",

        "Independent verification observations.",

        "Governance review intelligence.",

        "Allocator due diligence participation.",

        "External audit findings.",

        "Review registry management.",

        "Trust impact contribution.",

        "Public claim review records.",

        "Institutional reviewer classifications.",

        "Verification commentary infrastructure.",

    ]

    for responsibility in responsibilities:

        story.append(
            Paragraph(
                f"• {responsibility}",
                BODY_STYLE,
            )
        )

    story.append(
        Spacer(
            1,
            SPACE_LG,
        )
    )

    # --------------------------------------------------
    # INSTITUTIONAL REVIEW SURFACES
    # --------------------------------------------------

    story.append(
        Paragraph(
            "INSTITUTIONAL REVIEW SURFACES",
            SUBTITLE_STYLE,
        )
    )

    story.append(
        Spacer(
            1,
            SPACE_MD,
        )
    )

    review_surfaces = [

        "Institutional Review Registry.",

        "Review Submission Infrastructure.",

        "Public Review Intelligence.",

    ]

    for surface in review_surfaces:

        story.append(
            Paragraph(
                f"• {surface}",
                BODY_STYLE,
            )
        )

    story.append(
        Spacer(
            1,
            SPACE_LG,
        )
    )

    # --------------------------------------------------
    # INSTITUTIONAL REVIEW REGISTRY
    # --------------------------------------------------

    story.append(
        Paragraph(
            "INSTITUTIONAL REVIEW REGISTRY",
            SUBTITLE_STYLE,
        )
    )

    story.append(
        Spacer(
            1,
            SPACE_MD,
        )
    )

    story.append(
        Paragraph(
            "The Institutional Review Registry acts as the "
            "canonical repository of all public review records "
            "associated with publicly verifiable trading claims.",
            BODY_STYLE,
        )
    )

    story.append(
        Paragraph(
            "Institutional reviews are preserved as part of the "
            "public trust context of every reviewed claim.",
            BODY_STYLE,
        )
    )

    story.append(
        Paragraph(
            "The registry enables allocators and external "
            "participants to independently evaluate the governance "
            "posture and institutional observations surrounding "
            "public trust records.",
            BODY_STYLE,
        )
    )

    story.append(
        Spacer(
            1,
            SPACE_LG,
        )
    )

    # --------------------------------------------------
    # REVIEW SUBMISSION INFRASTRUCTURE
    # --------------------------------------------------

    story.append(PageBreak())

    story.append(
        Paragraph(
            "REVIEW SUBMISSION INFRASTRUCTURE",
            SUBTITLE_STYLE,
        )
    )

    story.append(
        Spacer(
            1,
            SPACE_MD,
        )
    )

    story.append(
        Paragraph(
            "The Review Submission Infrastructure provides "
            "standardized workflows for allocators, auditors, "
            "governance specialists and verification participants "
            "to submit institutional review statements.",
            BODY_STYLE,
        )
    )

    submission_capabilities = [

        "Institutional review submissions.",

        "Governance observations.",

        "Verification findings.",

        "Due diligence commentary.",

        "Allocator review participation.",

        "External audit submissions.",

    ]

    for capability in submission_capabilities:

        story.append(
            Paragraph(
                f"• {capability}",
                BODY_STYLE,
            )
        )

    story.append(
       Spacer(
            1,
            SPACE_LG,
        )
    )

    # --------------------------------------------------
    # PUBLIC REVIEW INTELLIGENCE
    # --------------------------------------------------

    story.append(
        Paragraph(
            "PUBLIC REVIEW INTELLIGENCE",
            SUBTITLE_STYLE,
        )
    )

    story.append(
        Spacer(
            1,
            SPACE_MD,
        )
    )

    story.append(
        Paragraph(
            "Public Review Intelligence aggregates review "
            "classifications, reviewer participation, trust "
            "implications and governance observations across the "
            "Public Trust Layer.",
            BODY_STYLE,
        )
    )

    review_intelligence = [

        "Review classifications.",

        "Reviewer participation.",

        "Trust impact metrics.",

        "Governance observations.",

        "Institutional review intelligence.",

        "Public trust augmentation metrics.",

    ]

    for intelligence in review_intelligence:

        story.append(
            Paragraph(
                f"• {intelligence}",
                BODY_STYLE,
            )
        )

    story.append(
        Paragraph(
            "The External Reviews domain enables institutional "
            "market participants to contribute independent trust "
            "intelligence surrounding publicly verifiable claims "
            "while preserving the integrity and canonical "
            "verification standards of the Trading Truth Layer.",
            BODY_STYLE,
        )
    )

    story.append(
        Spacer(
            1,
            SPACE_LG,
        )
    )

        # --------------------------------------------------
    # EVIDENCE GRAPH
    # --------------------------------------------------

    story.append(PageBreak())

    story.append(
        Paragraph(
            "EVIDENCE GRAPH",
            SUBTITLE_STYLE,
        )
    )

    story.append(
        Spacer(
            1,
            SPACE_MD,
        )
    )

    story.append(
        Paragraph(
            "The Evidence Graph represents the institutional "
            "relationship intelligence engine of the Public Trust "
            "Layer.",
            BODY_STYLE,
        )
    )

    story.append(
        Paragraph(
            "It exposes the canonical evidence network connecting "
            "claims, trades, ledgers, broker records, audit events, "
            "integrity alerts, reviews and governance relationships.",
            BODY_STYLE,
        )
    )

    story.append(
        Paragraph(
            "Rather than viewing a trading claim as an isolated "
            "performance output, the Evidence Graph enables "
            "institutional participants to investigate the entire "
            "evidence chain supporting publicly verifiable claims.",
            BODY_STYLE,
        )
    )

    story.append(
        Paragraph(
            "The Evidence Graph provides graph-based investigation "
            "capabilities designed for allocators, auditors, "
            "governance reviewers and verification specialists "
            "performing institutional due diligence.",
            BODY_STYLE,
        )
    )

    story.append(
        Spacer(
            1,
            SPACE_LG,
        )
    )

    # --------------------------------------------------
    # PRIMARY RESPONSIBILITIES
    # --------------------------------------------------

    story.append(
        Paragraph(
            "PRIMARY RESPONSIBILITIES",
            SUBTITLE_STYLE,
        )
    )

    story.append(
        Spacer(
            1,
            SPACE_MD,
        )
    )

    responsibilities = [

        "Evidence relationship intelligence.",

        "Claim investigation infrastructure.",

        "Trade lineage visualization.",

        "Evidence chain analysis.",

        "Integrity monitoring.",

        "Governance relationship mapping.",

        "Risk path analysis.",

        "Critical evidence discovery.",

        "Graph-based investigations.",

        "Institutional due diligence workflows.",

    ]

    for responsibility in responsibilities:

        story.append(
            Paragraph(
                f"• {responsibility}",
                BODY_STYLE,
            )
        )

    story.append(
        Spacer(
            1,
            SPACE_LG,
        )
    )

    # --------------------------------------------------
    # INSTITUTIONAL INVESTIGATION SURFACES
    # --------------------------------------------------

    story.append(
        Paragraph(
            "INSTITUTIONAL INVESTIGATION SURFACES",
            SUBTITLE_STYLE,
        )
    )

    story.append(
        Spacer(
            1,
            SPACE_MD,
        )
    )

    investigation_surfaces = [

        "Claim Registry.",

        "Investigation Inspector.",

        "Investigation Canvas.",

        "Evidence Exceptions.",

        "Evidence Infrastructure.",

    ]

    for surface in investigation_surfaces:

        story.append(
            Paragraph(
                f"• {surface}",
                BODY_STYLE,
            )
        )

    story.append(
        Spacer(
            1,
            SPACE_LG,
        )
    )

    # --------------------------------------------------
    # CLAIM REGISTRY
    # --------------------------------------------------

    story.append(
        Paragraph(
            "CLAIM REGISTRY",
            SUBTITLE_STYLE,
        )
    )

    story.append(
        Spacer(
            1,
            SPACE_MD,
        )
    )

    story.append(
        Paragraph(
            "The Claim Registry provides institutional access to "
            "publicly investigable claims and their associated "
            "evidence relationships.",
            BODY_STYLE,
        )
    )

    story.append(
        Paragraph(
            "The registry establishes the institutional entry "
            "point for graph-based investigations across the "
            "Public Trust Layer.",
            BODY_STYLE,
        )
    )

    story.append(
        Spacer(
            1,
            SPACE_LG,
        )
    )

    # --------------------------------------------------
    # INVESTIGATION INSPECTOR
    # --------------------------------------------------

    story.append(
        Paragraph(
            "INVESTIGATION INSPECTOR",
            SUBTITLE_STYLE,
        )
    )

    story.append(
        Spacer(
            1,
            SPACE_MD,
        )
    )

    inspector_capabilities = [

        "Relationship density metrics.",

        "Evidence coverage intelligence.",

        "Institutional investigation statistics.",

        "Governance intelligence.",

        "Evidence chain visibility.",

        "Allocator investigation metrics.",

    ]

    for capability in inspector_capabilities:

        story.append(
            Paragraph(
                f"• {capability}",
                BODY_STYLE,
            )
        )

    story.append(
        Paragraph(
            "The Investigation Inspector provides executive "
            "institutional intelligence regarding the evidence "
            "network supporting publicly verifiable claims.",
            BODY_STYLE,
        )
    )

    story.append(
        Spacer(
            1,
            SPACE_LG,
        )
    )

    # --------------------------------------------------
    # INVESTIGATION CANVAS
    # --------------------------------------------------

    story.append(
        Paragraph(
            "INVESTIGATION CANVAS",
            SUBTITLE_STYLE,
        )
    )

    story.append(
        Spacer(
            1,
            SPACE_MD,
        )
    )

    story.append(
        Paragraph(
            "The Investigation Canvas provides an interactive "
            "institutional evidence network allowing reviewers "
            "to investigate claim lineage, audit trails and "
            "governance dependencies.",
            BODY_STYLE,
        )
    )

    canvas_capabilities = [

        "Evidence relationship visualization.",

        "Trade lineage investigations.",

        "Audit trail analysis.",

        "Governance dependency mapping.",

        "Institutional due diligence investigations.",

    ]

    for capability in canvas_capabilities:

        story.append(
            Paragraph(
                f"• {capability}",
                BODY_STYLE,
            )
        )

    story.append(
        Spacer(
            1,
            SPACE_LG,
        )
    )

    # --------------------------------------------------
    # EVIDENCE EXCEPTIONS
    # --------------------------------------------------

    story.append(PageBreak())

    story.append(
        Paragraph(
            "EVIDENCE EXCEPTIONS",
            SUBTITLE_STYLE,
        )
    )

    story.append(
        Spacer(
            1,
            SPACE_MD,
        )
    )

    evidence_exceptions = [

        "Integrity failures.",

        "Missing evidence.",

        "Evidence protection gaps.",

        "Governance exceptions.",

        "Verification exceptions.",

        "Critical investigation alerts.",

    ]

    for exception in evidence_exceptions:

        story.append(
            Paragraph(
                f"• {exception}",
                BODY_STYLE,
            )
        )

    story.append(
       Paragraph(
            "Evidence Exceptions highlight institutional concerns "
            "identified during graph-based investigations.",
            BODY_STYLE,
        )
    )

    story.append(
        Spacer(
            1,
            SPACE_LG,
        )
    )

    # --------------------------------------------------
    # EVIDENCE INFRASTRUCTURE
    # --------------------------------------------------

    story.append(
        Paragraph(
            "EVIDENCE INFRASTRUCTURE",
            SUBTITLE_STYLE,
        )
    )

    story.append(
        Spacer(
            1,
            SPACE_MD,
        )
    )

    infrastructure_metrics = [

        "Subsystem readiness intelligence.",

        "Evidence architecture intelligence.",

        "Verification infrastructure intelligence.",

        "Institutional coverage metrics.",

        "Governance infrastructure monitoring.",

    ]

    for metric in infrastructure_metrics:

        story.append(
            Paragraph(
                f"• {metric}",
                BODY_STYLE,
            )
        )

    story.append(
        Paragraph(
            "The Evidence Graph enables institutional participants "
            "to investigate not only what a claim reports, but how "
            "every public record is connected, verified and "
            "governed across the Trading Truth Layer evidence "
            "network.",
            BODY_STYLE,
        )
    )

    story.append(
        Spacer(
            1,
            SPACE_LG,
        )
    )

        # --------------------------------------------------
    # PUBLIC PROFILES
    # --------------------------------------------------

    story.append(
        Paragraph(
            "PUBLIC PROFILES",
            SUBTITLE_STYLE,
        )
    )

    story.append(
        Spacer(
            1,
            SPACE_MD,
        )
    )

    story.append(
        Paragraph(
            "The Public Profiles domain represents the issuer-level "
            "trust surface of the Public Trust Layer.",
            BODY_STYLE,
        )
    )

    story.append(
        Paragraph(
            "It aggregates publicly verifiable claims, trust "
            "metrics, network credibility, governance posture and "
            "historical claim performance into an institutional "
            "trust profile.",
            BODY_STYLE,
        )
    )

    story.append(
        Paragraph(
            "Public Profiles provide allocators and institutional "
            "participants with a high-level trust view of a trading "
            "entity rather than requiring independent analysis of "
            "every individual claim.",
            BODY_STYLE,
        )
    )

    story.append(
        Paragraph(
            "The Public Profile serves as the canonical public "
            "representation of an issuer's historical verification "
            "quality, governance standards and public trust posture "
            "across all publicly exposed claims.",
            BODY_STYLE,
        )
    )

    story.append(
        Spacer(
            1,
            SPACE_LG,
        )
    )

    # --------------------------------------------------
    # PRIMARY RESPONSIBILITIES
    # --------------------------------------------------

    story.append(
        Paragraph(
            "PRIMARY RESPONSIBILITIES",
            SUBTITLE_STYLE,
        )
    )

    story.append(
        Spacer(
            1,
            SPACE_MD,
        )
    )

    responsibilities = [

        "Issuer-level trust aggregation.",

        "Public trust profile generation.",

        "Locked claim aggregation.",

        "Historical trust analysis.",

        "Network credibility assessment.",

        "Public claim distribution.",

        "Profile-level governance intelligence.",

        "Institutional trust ranking.",

        "Public trust widgets.",

        "Verification profile management.",

    ]

    for responsibility in responsibilities:

        story.append(
            Paragraph(
                f"• {responsibility}",
                BODY_STYLE,
            )
        )

    story.append(
        Spacer(
            1,
            SPACE_LG,
        )
    )

    # --------------------------------------------------
    # INSTITUTIONAL TRUST SURFACES
    # --------------------------------------------------

    story.append(
        Paragraph(
            "INSTITUTIONAL TRUST SURFACES",
            SUBTITLE_STYLE,
        )
    )

    story.append(
        Spacer(
            1,
            SPACE_MD,
        )
    )

    trust_surfaces = [

        "Trust Widget.",

        "Issuer Identity.",

        "Profile Trust Context.",

        "Claims Under Profile.",

        "Public Distribution Infrastructure.",

    ]

    for surface in trust_surfaces:

        story.append(
            Paragraph(
                f"• {surface}",
                BODY_STYLE,
            )
        )

    story.append(
        Spacer(
            1,
            SPACE_LG,
        )
    )

    # --------------------------------------------------
    # TRUST WIDGET
    # --------------------------------------------------

    story.append(
        Paragraph(
            "TRUST WIDGET",
            SUBTITLE_STYLE,
        )
    )

    story.append(
        Spacer(
            1,
            SPACE_MD,
        )
    )

    story.append(
        Paragraph(
            "The Trust Widget provides embeddable institutional "
            "trust metrics that may be distributed across external "
            "websites, communities and verification surfaces.",
            BODY_STYLE,
        )
    )

    trust_widget_capabilities = [

        "Institutional trust scores.",

        "Verification bands.",

        "Network credibility metrics.",

        "Allocator readiness indicators.",

        "Public verification access.",

    ]

    for capability in trust_widget_capabilities:

        story.append(
            Paragraph(
                f"• {capability}",
                BODY_STYLE,
            )
        )

    story.append(
        Spacer(
            1,
            SPACE_LG,
        )
    )

    # --------------------------------------------------
    # ISSUER IDENTITY
    # --------------------------------------------------

    story.append(
        Paragraph(
            "ISSUER IDENTITY",
            SUBTITLE_STYLE,
        )
    )

    story.append(
        Spacer(
            1,
            SPACE_MD,
        )
    )

    story.append(
        Paragraph(
            "The Issuer Identity surface acts as the canonical "
            "public identity layer representing the issuer's "
            "institutional trust posture.",
            BODY_STYLE,
        )
    )

    issuer_identity = [

        "Institutional identity information.",

        "Verification profile information.",

        "Historical trust posture.",

        "Public trust visibility metrics.",

        "Network credibility indicators.",

    ]

    for item in issuer_identity:

        story.append(
            Paragraph(
                f"• {item}",
                BODY_STYLE,
            )
        )

    story.append(
        Spacer(
            1,
            SPACE_LG,
        )
    )

    # --------------------------------------------------
    # PROFILE TRUST CONTEXT
    # --------------------------------------------------

    story.append(
        Paragraph(
            "PROFILE TRUST CONTEXT",
            SUBTITLE_STYLE,
        )
    )

    story.append(
        Spacer(
            1,
            SPACE_MD,
        )
    )

    profile_context = [

        "Aggregated trust metrics.",

        "Governance intelligence.",

        "Historical verification quality.",

        "Institutional credibility intelligence.",

        "Network trust metrics.",

        "Allocator confidence indicators.",

    ]

    for item in profile_context:

        story.append(
            Paragraph(
                f"• {item}",
                BODY_STYLE,
            )
        )

    story.append(
        Paragraph(
            "Profile Trust Context aggregates claim-level trust "
            "metrics into issuer-level governance and credibility "
            "intelligence.",
            BODY_STYLE,
        )
    )

    story.append(
        Spacer(
            1,
            SPACE_LG,
        )
    )

    # --------------------------------------------------
    # CLAIMS UNDER PROFILE
    # --------------------------------------------------

    story.append(
        Paragraph(
            "CLAIMS UNDER PROFILE",
            SUBTITLE_STYLE,
        )
    )

    story.append(
        Spacer(
            1,
            SPACE_MD,
        )
    )

    claims_under_profile = [

        "Publicly locked claims.",

        "Verification status information.",

        "Trust intelligence metrics.",

        "Historical performance records.",

        "Canonical verification routes.",

        "Publication metadata.",

    ]

    for item in claims_under_profile:

        story.append(
            Paragraph(
                f"• {item}",
                BODY_STYLE,
            )
        )

    story.append(
       Paragraph(
            "This institutional surface provides allocators with "
            "access to all publicly exposed claims contributing to "
            "the issuer's trust profile.",
            BODY_STYLE,
        )
    )

    story.append(
        Spacer(
            1,
            SPACE_LG,
        )
    )

    # --------------------------------------------------
    # PUBLIC DISTRIBUTION INFRASTRUCTURE
    # --------------------------------------------------

    story.append(
        Paragraph(
            "PUBLIC DISTRIBUTION INFRASTRUCTURE",
            SUBTITLE_STYLE,
        )
    )

    story.append(
        Spacer(
            1,
            SPACE_MD,
        )
    )

    distribution_capabilities = [

        "Public verification distribution.",

        "Claim discovery infrastructure.",

        "Institutional trust dissemination.",

        "Public profile publication.",

        "External verification access.",

        "Allocator accessibility infrastructure.",

    ]

    for capability in distribution_capabilities:

        story.append(
            Paragraph(
                f"• {capability}",
                BODY_STYLE,
            )
        )

    story.append(
        Paragraph(
            "The Public Distribution Infrastructure enables public "
            "verification, claim discovery and institutional trust "
            "dissemination across the Trading Truth Layer ecosystem.",
            BODY_STYLE,
        )
    )

    story.append(
        Spacer(
            1,
            SPACE_LG,
        )
    )


        # --------------------------------------------------
    # INSTITUTIONAL QUESTIONS ANSWERED
    # --------------------------------------------------

    story.append(
        Paragraph(
            "INSTITUTIONAL QUESTIONS ANSWERED",
            SUBTITLE_STYLE,
        )
    )

    story.append(
        Spacer(
            1,
            SPACE_MD,
        )
    )

    institutional_questions = [

        "Can this claim be independently verified by external institutions?",

        "Has the claim been publicly published and institutionally exposed?",

        "What is the public trust posture of the issuer?",

        "Can allocators independently assess the verification infrastructure?",

        "Are institutional review records available for allocator due diligence?",

        "Is the public trust infrastructure publication-ready?",

        "Does the claim preserve evidence lineage and governance standards?",

        "Can institutional participants investigate the entire evidence network?",

        "Is the issuer institutionally credible across all publicly exposed claims?",

        "Can public trust records be distributed across global capital markets?",

    ]

    for question in institutional_questions:

        story.append(
            Paragraph(
                f"• {question}",
                BODY_STYLE,
            )
        )

    story.append(
        Spacer(
            1,
            SPACE_LG,
        )
    )

    # --------------------------------------------------
    # TTL WORKFLOW POSITION
    # --------------------------------------------------

    story.append(PageBreak())

    story.append(
        Paragraph(
            "TTL WORKFLOW POSITION",
            SUBTITLE_STYLE,
        )
    )

    story.append(
        Spacer(
            1,
            SPACE_MD,
        )
    )

    workflow = [

        "Institutional Evidence Infrastructure",

        "Canonical Evidence Infrastructure",

        "Institutional Claim Governance Infrastructure",

        "Trust Intelligence Infrastructure",

        "Institutional Investigation Infrastructure",

        "Public Trust Layer",

    ]

    for item in workflow:

        story.append(
            Paragraph(
                item,
                BODY_CENTER_STYLE,
            )
        )

        story.append(
            Spacer(
                1,
                SPACE_MD,
            )
        )

    story.append(
        Paragraph(
            "The Public Trust Layer represents the final public "
            "trust distribution layer of the Trading Truth Layer "
            "institutional trust lifecycle.",
            BODY_STYLE,
        )
    )

    story.append(
        Spacer(
            1,
            SPACE_LG,
        )
    )

    # --------------------------------------------------
    # FUTURE INFRASTRUCTURE CAPABILITIES
    # --------------------------------------------------

    story.append(
        Paragraph(
            "FUTURE INFRASTRUCTURE CAPABILITIES",
            SUBTITLE_STYLE,
        )
    )

    story.append(
        Spacer(
            1,
            SPACE_MD,
        )
    )

    future_capabilities = [

        "Global public trust registries.",

        "Institutional trust distribution networks.",

        "Cross-platform trust intelligence widgets.",

        "Allocator-specific public verification infrastructure.",

        "Institutional trust APIs.",

        "Public trust syndication infrastructure.",

        "Advanced graph-based due diligence capabilities.",

        "Global issuer trust rankings.",

        "Institutional review ecosystems.",

        "Public trust infrastructure automation.",

    ]

    for capability in future_capabilities:

        story.append(
            Paragraph(
                f"• {capability}",
                BODY_STYLE,
            )
        )

    story.append(
        Spacer(
            1,
            SPACE_LG,
        )
    )

    # --------------------------------------------------
    # DOMAIN VII ARCHITECTURE STATUS
    # --------------------------------------------------

    story.append(PageBreak())

    story.append(
        Paragraph(
            "DOMAIN VII ARCHITECTURE STATUS",
            SUBTITLE_STYLE,
        )
    )

    story.append(
        Spacer(
            1,
            SPACE_MD,
        )
    )

    architecture_components = [

        "Public Records.",

        "Verification Routes.",

        "Trust Directory.",

        "Verification Network.",

        "External Reviews.",

        "Evidence Graph.",

        "Public Profiles.",

    ]

    for component in architecture_components:

        story.append(
            Paragraph(
                f"• {component}",
                BODY_STYLE,
            )
        )

    story.append(
        Paragraph(
            "These institutional trust surfaces collectively "
            "establish the Public Trust Infrastructure of the "
            "Trading Truth Layer.",
            BODY_STYLE,
        )
    )

    story.append(
        Spacer(
            1,
            SPACE_LG,
        )
    )

    # --------------------------------------------------
    # ARCHITECTURE SUMMARY
    # --------------------------------------------------

    story.append(
        Paragraph(
            "ARCHITECTURE SUMMARY",
            SUBTITLE_STYLE,
        )
    )

    story.append(
        Spacer(
            1,
            SPACE_MD,
        )
    )

    summary_points = [

        "Transforms institutionally verified claims into publicly verifiable trust records.",

        "Provides canonical public verification infrastructure.",

        "Enables allocator-friendly trust discovery and institutional due diligence.",

        "Supports graph-based institutional investigations.",

        "Provides independent institutional review capabilities.",

        "Aggregates issuer-level public trust intelligence.",

        "Distributes institutional trust across public verification surfaces.",

        "Acts as the public trust distribution layer of Trading Truth Layer.",

    ]

    for point in summary_points:

        story.append(
            Paragraph(
                f"• {point}",
                BODY_STYLE,
            )
        )

    story.append(
        Paragraph(
            "The Public Trust Layer represents the culmination of "
            "the institutional verification pipeline by enabling "
            "global institutions to independently discover, "
            "verify, investigate and assess publicly exposed "
            "trading records without compromising institutional "
            "governance standards.",
            BODY_STYLE,
        )
    )

    story.append(
       Spacer(
            1,
            SPACE_LG,
        )
    )

    # --------------------------------------------------
    # PAGE BREAK
    # --------------------------------------------------

    story.append(
        PageBreak()
    )

    return story


# ==========================================================
# END OF FILE
# ==========================================================