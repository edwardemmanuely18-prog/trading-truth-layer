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


def build_domain_4_claim_operations():

    """
    Builds Domain IV documentation for the
    Institutional Claim Governance Infrastructure.
    """

    story = []

    # --------------------------------------------------
    # DOMAIN TITLE
    # --------------------------------------------------

    story.append(
        Paragraph(
            "DOMAIN IV",
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
            "INSTITUTIONAL CLAIM GOVERNANCE INFRASTRUCTURE",
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
            "(CLAIM OPERATIONS)",
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
            "The Institutional Claim Governance Infrastructure is "
            "the domain responsible for transforming canonical "
            "trading evidence into lifecycle-governed verification "
            "records.",
            BODY_STYLE,
        )
    )

    story.append(
        Paragraph(
            "Claims are not user reported performance statements.",
            BODY_STYLE,
        )
    )

    story.append(
        Paragraph(
            "Claims are governed institutional records that define "
            "verification scope, evidence universe, visibility "
            "posture, integrity state, claim methodology, version "
            "lineage, lifecycle progression and public trust "
            "eligibility.",
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
    # WHY DOES IT EXIST?
    # --------------------------------------------------

    story.append(
        Paragraph(
            "WHY DOES IT EXIST?",
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
            "Institutional trust requires governed verification "
            "records rather than user generated performance "
            "statements.",
            BODY_STYLE,
        )
    )

    story.append(
        Paragraph(
            "The Institutional Claim Governance Infrastructure "
            "exists to transform canonical evidence into "
            "institutionally defensible claims capable of "
            "participating in public trust workflows.",
            BODY_STYLE,
        )
    )

    story.append(
        Paragraph(
            "Every public verification record produced by Trading "
            "Truth Layer originates from this governance "
            "infrastructure.",
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
    # WHICH INSTITUTIONAL PROBLEMS DOES IT SOLVE?
    # --------------------------------------------------

    story.append(
        Paragraph(
            "WHICH INSTITUTIONAL PROBLEMS DOES IT SOLVE?",
            SUBTITLE_STYLE,
        )
    )

    story.append(
        Spacer(
            1,
            SPACE_MD,
        )
    )

    problems = [

        "Unverified public trading claims.",

        "Unknown claim methodologies.",

        "Missing lifecycle governance.",

        "Silent evidence modification.",

        "Lack of institutional claim lineage.",

        "Poor public trust controls.",

        "Insufficient audit capabilities.",

        "Missing verification workflows.",

    ]

    for problem in problems:

        story.append(
            Paragraph(
                f"• {problem}",
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
    # CLAIM GOVERNANCE PRINCIPLES
    # --------------------------------------------------

    story.append(
        Paragraph(
            "CLAIM GOVERNANCE PRINCIPLES",
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
            "Trading Truth Layer governs every claim throughout "
            "its institutional lifecycle.",
            BODY_STYLE,
        )
    )

    story.append(
        Paragraph(
            "Claims are versioned, lifecycle-governed and "
            "institutionally auditable verification records.",
            BODY_STYLE,
        )
    )

    story.append(
        Paragraph(
            "No claim may bypass verification, publication or "
            "locking requirements before becoming eligible for "
            "institutional public trust exposure.",
            BODY_STYLE,
        )
    )

    story.append(
        Paragraph(
            "Institutional integrity is preserved through "
            "cryptographic hashing, immutable trade set "
            "fingerprints and controlled lifecycle progression.",
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

        "Claim Builder",

        "Claim Library",

        "Evidence Review",

        "Schema Registry",

        "Templates",

    ]

    for subdomain in subdomains:

        story.append(
            Paragraph(
                f"• {subdomain}",
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
    # CLAIM BUILDER
    # --------------------------------------------------

    story.append(
        Paragraph(
            "CLAIM BUILDER",
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
            "The Claim Builder is the institutional entry point "
            "for all claim creation operations inside Trading "
            "Truth Layer.",
            BODY_STYLE,
        )
    )

    story.append(
        Paragraph(
            "Every institutional claim is created through the "
            "Claim Schema Builder.",
            BODY_STYLE,
        )
    )

    story.append(
        Paragraph(
            "The Claim Schema Builder guides users through all "
            "required information necessary to define a "
            "verification-ready claim.",
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
    # CLAIM SCHEMA DEFINITION
    # --------------------------------------------------

    story.append(PageBreak())

    story.append(
        Paragraph(
            "CLAIM SCHEMA DEFINITION",
            SUBTITLE_STYLE,
        )
    )

    story.append(
        Spacer(
            1,
            SPACE_MD,
        )
    )

    schema_items = [

        "Claim name.",

        "Verification period.",

        "Included member IDs.",

        "Included trading symbols.",

        "Excluded trade IDs.",

        "Initial visibility posture.",

        "Methodology notes.",

        "Verification scope configuration.",

    ]

    for item in schema_items:

        story.append(
            Paragraph(
                f"• {item}",
                BODY_STYLE,
            )
        )

    story.append(
        Paragraph(
            "The claim schema determines the exact evidence "
            "universe that participates in institutional claim "
            "computation and verification.",
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
    # CLAIM LIBRARY
    # --------------------------------------------------

    story.append(
        Paragraph(
            "CLAIM LIBRARY",
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
            "The Claim Library serves as the institutional registry "
            "for all lifecycle-governed claims contained within a "
            "workspace.",
            BODY_STYLE,
        )
    )

    story.append(
        Paragraph(
            "Every claim produced by Trading Truth Layer is "
            "cataloged and continuously governed throughout its "
            "institutional lifecycle.",
            BODY_STYLE,
        )
    )

    story.append(
        Paragraph(
            "The Claim Library provides executive visibility into "
            "verification status, publication posture, public "
            "routing capabilities and institutional performance "
            "metrics.",
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
    # CLAIM LIBRARY CAPABILITIES
    # --------------------------------------------------

    story.append(
        Paragraph(
            "CLAIM LIBRARY CAPABILITIES",
            SUBTITLE_STYLE,
        )
    )

    story.append(
        Spacer(
            1,
            SPACE_MD,
        )
    )

    library_capabilities = [

        "Lifecycle monitoring.",

        "Claim registry management.",

        "Public route readiness monitoring.",

        "Performance overview.",

        "Verification status monitoring.",

        "Institutional evidence routing.",

        "Public trust exposure controls.",

    ]

    for capability in library_capabilities:

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
    # CLAIM PERFORMANCE METRICS
    # --------------------------------------------------

    story.append(
        Paragraph(
            "CLAIM PERFORMANCE METRICS",
            SUBTITLE_STYLE,
        )
    )

    story.append(
        Spacer(
            1,
            SPACE_MD,
        )
    )

    metrics = [

        "Trade count.",

        "Net profitability.",

        "Profit factor.",

        "Win rate.",

        "Verification scope.",

        "Lifecycle timestamps.",

        "Claim hashes.",

        "Trade set hashes.",

        "Member rankings.",

    ]

    for metric in metrics:

        story.append(
            Paragraph(
                f"• {metric}",
                BODY_STYLE,
            )
        )

    story.append(
        Paragraph(
            "All institutional performance metrics are computed "
            "directly from canonical evidence records contained "
            "within the claim verification scope.",
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
    # EVIDENCE REVIEW
    # --------------------------------------------------

    story.append(
        Paragraph(
            "EVIDENCE REVIEW",
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
            "The Evidence Review subdomain provides institutional "
            "evidence inspection capabilities prior to claim "
            "verification.",
            BODY_STYLE,
        )
    )

    story.append(
        Paragraph(
            "Users may inspect every trade participating in a "
            "claim's evidence universe before progressing through "
            "the institutional lifecycle.",
            BODY_STYLE,
        )
    )

    story.append(
        Paragraph(
            "Institutional evidence review ensures that claim "
            "construction remains transparent and auditable.",
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
    # EVIDENCE REVIEW CAPABILITIES
    # --------------------------------------------------

    story.append(
        Paragraph(
            "EVIDENCE REVIEW CAPABILITIES",
            SUBTITLE_STYLE,
        )
    )

    story.append(
        Spacer(
            1,
            SPACE_MD,
        )
    )

    review_capabilities = [

        "Trade-level evidence inspection.",

        "Trust tier visibility.",

        "Verification status review.",

        "Claim scope validation.",

        "Evidence lineage inspection.",

        "Institutional audit review.",

    ]

    for capability in review_capabilities:

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
    # SCHEMA REGISTRY
    # --------------------------------------------------

    story.append(
        Paragraph(
            "SCHEMA REGISTRY",
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
            "The Schema Registry provides institutional claim "
            "schema governance capabilities.",
            BODY_STYLE,
        )
    )

    story.append(
        Paragraph(
            "Every claim schema produced within Trading Truth Layer "
            "is governed throughout its institutional lifecycle.",
            BODY_STYLE,
        )
    )

    story.append(
        Paragraph(
            "Institutional schema governance guarantees that all "
            "verification records remain version-aware and "
            "institutionally auditable.",
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
    # CLAIM LIFECYCLE GOVERNANCE
    # --------------------------------------------------

    story.append(
        Paragraph(
            "CLAIM LIFECYCLE GOVERNANCE",
            SUBTITLE_STYLE,
        )
    )

    story.append(
        Spacer(
            1,
            SPACE_MD,
        )
    )

    lifecycle_states = [

        "Draft.",

        "Verified.",

        "Published.",

        "Locked.",

    ]

    for state in lifecycle_states:

        story.append(
            Paragraph(
                f"• {state}",
                BODY_STYLE,
            )
        )

    story.append(
       Paragraph(
            "Every institutional claim progresses through these "
            "lifecycle stages before becoming eligible for public "
            "trust distribution.",
            BODY_STYLE,
        )
    )

    story.append(
        Paragraph(
            "Locked claims become institutionally immutable and "
            "preserve their evidence universe permanently.",
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
    # TEMPLATES
    # --------------------------------------------------

    story.append(
        Paragraph(
            "TEMPLATES",
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
            "The Templates subdomain provides reusable institutional "
            "claim configurations for common verification workflows.",
            BODY_STYLE,
        )
    )

    story.append(
        Paragraph(
            "Templates accelerate claim construction while preserving "
            "institutional governance requirements and verification "
            "standards.",
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
    # INSTITUTIONAL OUTPUTS
    # --------------------------------------------------

    story.append(PageBreak())

    story.append(
        Paragraph(
            "INSTITUTIONAL OUTPUTS",
            SUBTITLE_STYLE,
        )
    )

    story.append(
        Spacer(
            1,
            SPACE_MD,
        )
    )

    outputs = [

        "Lifecycle-governed claims.",

        "Verification-ready claim schemas.",

        "Institutional performance records.",

        "Public trust eligible claims.",

        "Claim lineage records.",

        "Institutional evidence scopes.",

        "Immutable locked claim records.",

        "Claim integrity hashes.",

    ]

    for output in outputs:

        story.append(
            Paragraph(
                f"• {output}",
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
    # TTL ECOSYSTEM INTERACTION
    # --------------------------------------------------

    story.append(
        Paragraph(
            "TTL ECOSYSTEM INTERACTION",
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
            "The Institutional Claim Governance Infrastructure "
            "consumes canonical evidence records produced by the "
            "Canonical Evidence Infrastructure.",
            BODY_STYLE,
        )
    )

    story.append(
        Paragraph(
            "Verified claims subsequently participate in Trust "
            "Intelligence analysis, institutional investigations "
            "and public trust distribution workflows.",
            BODY_STYLE,
        )
    )

    story.append(
        Paragraph(
            "Claims therefore represent the institutional bridge "
            "between governed trading evidence and publicly "
            "verifiable trust artifacts.",
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

        "Institutional claim templates.",

        "Advanced claim methodologies.",

        "Multi-claim aggregation capabilities.",

        "Automated claim recommendations.",

        "Portfolio-level claim construction.",

        "Institutional benchmark comparisons.",

        "Enhanced public trust routing capabilities.",

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

    architecture_summary = [

        "Consumes canonical evidence records.",

        "Constructs lifecycle-governed claims.",

        "Defines institutional verification scope.",

        "Preserves claim lineage and integrity.",

        "Governs institutional claim lifecycles.",

        "Produces public trust eligible records.",

        "Provides immutable locked verification artifacts.",

    ]

    for item in architecture_summary:

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
    # TTL WORKFLOW POSITION
    # --------------------------------------------------

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

        "Canonical Evidence Infrastructure",

        "Institutional Claim Governance Infrastructure",

        "Trust Intelligence Infrastructure",

        "Institutional Investigation Infrastructure",

        "Public Trust Infrastructure",

    ]

    for step in workflow:

        story.append(
            Paragraph(
                step,
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