"""
Trading Truth Layer (TTL)
Institutional Evidence Graph Engine

Canonical Graph Edge Factory

Every relationship inside the Evidence Graph MUST be created
through this module.

Never manually create edge dictionaries.
"""

from datetime import datetime
from typing import Any, Dict, Optional

from .graph_relationships import (
    ALL_RELATIONSHIPS,
    CONFIDENCE_VERIFIED,
)


#
# ---------------------------------------------------------------------
# Edge Styles
# ---------------------------------------------------------------------
#

EDGE_STYLES = {

    "GENERATED_FROM":
        "solid",

    "IMPORTED_FROM":
        "solid",

    "SYNCED_FROM":
        "solid",

    "BELONGS_TO":
        "solid",

    "LINKED_TO":
        "solid",

    "USES":
        "dashed",

    "CONNECTED_TO":
        "dashed",

    "HAS_HASH":
        "solid",

    "HAS_FINGERPRINT":
        "solid",

    "HAS_EXCEPTION":
        "dotted",

    "FLAGGED_BY":
        "dotted",

    "SCANNED_BY":
        "solid",

    "VERIFIED_BY":
        "solid",

    "LOCKED_BY":
        "solid",

    "PUBLISHED_BY":
        "solid",

    "UPDATED_BY":
        "dashed",

    "CREATED_BY":
        "dashed",

    "EXECUTED_ON":
        "solid",

    "PRODUCED":
        "solid",
}


#
# ---------------------------------------------------------------------
# Relationship Validation
# ---------------------------------------------------------------------
#

def validate_relationship(
    relationship: str,
):

    if relationship not in ALL_RELATIONSHIPS:

        raise ValueError(

            f"Unsupported relationship: {relationship}"

        )


#
# ---------------------------------------------------------------------
# Canonical Edge Builder
# ---------------------------------------------------------------------
#

def build_edge(

    edge_id: str,

    source: str,

    target: str,

    relationship: str,

    *,

    confidence: str = CONFIDENCE_VERIFIED,

    created_at: Optional[datetime] = None,

    weight: float = 1.0,

    directional: bool = True,

    metadata: Optional[Dict[str, Any]] = None,

):

    validate_relationship(
        relationship
    )

    metadata = metadata or {}

    return {

        "id":
            edge_id,

        "source":
            source,

        "target":
            target,

        "relationship":
            relationship,

        "confidence":
            confidence,

        "directional":
            directional,

        "weight":
            weight,

        "style":
            EDGE_STYLES.get(

                relationship,

                "solid",

            ),

        "created_at":
            (
                created_at.isoformat()
                if isinstance(
                    created_at,
                    datetime,
                )
                else created_at
            ),

        "metadata":
            metadata,

    }


#
# ---------------------------------------------------------------------
# Duplicate Detection
# ---------------------------------------------------------------------
#

def edge_signature(

    edge,

):

    return (

        edge["source"],

        edge["target"],

        edge["relationship"],

    )


def deduplicate_edges(

    edges,

):

    unique = {}

    for edge in edges:

        unique[
            edge_signature(edge)
        ] = edge

    return list(

        unique.values()

    )


#
# ---------------------------------------------------------------------
# Edge Metrics
# ---------------------------------------------------------------------
#

def relationship_statistics(

    edges,

):

    stats = {}

    for edge in edges:

        relationship = edge[
            "relationship"
        ]

        stats[
            relationship
        ] = (
            stats.get(
                relationship,
                0,
            )
            + 1
        )

    return stats


#
# ---------------------------------------------------------------------
# Convenience Builders
# ---------------------------------------------------------------------
#

def link(

    source,

    target,

    relationship,

    **kwargs,

):

    edge_id = (

        f"{source}"

        "_"

        f"{relationship}"

        "_"

        f"{target}"

    )

    return build_edge(

        edge_id=edge_id,

        source=source,

        target=target,

        relationship=relationship,

        **kwargs,

    )


#
# ---------------------------------------------------------------------
# Graph Validation
# ---------------------------------------------------------------------
#

def validate_graph(

    nodes,

    edges,

):

    node_ids = {

        node["id"]

        for node in nodes

    }

    invalid = []

    for edge in edges:

        if (

            edge["source"]

            not in node_ids

        ):

            invalid.append(

                edge

            )

            continue

        if (

            edge["target"]

            not in node_ids

        ):

            invalid.append(

                edge

            )

    return invalid