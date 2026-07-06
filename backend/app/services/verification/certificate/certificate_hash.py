from __future__ import annotations

import hashlib
import json
from typing import Any


def generate_certificate_hash(
    payload: dict[str, Any],
) -> str:
    """
    Canonical hash for every verification
    certificate.
    """

    canonical = json.dumps(

        payload,

        sort_keys=True,

        default=str,

        separators=(",", ":"),

    )

    return hashlib.sha256(

        canonical.encode("utf-8")

    ).hexdigest()