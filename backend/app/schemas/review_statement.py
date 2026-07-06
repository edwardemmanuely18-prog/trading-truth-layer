from pydantic import BaseModel
from typing import Optional


class ReviewStatementCreate(
    BaseModel
):
    claim_schema_id: int

    reviewer_name: str

    reviewer_organization: Optional[
        str
    ] = None

    reviewer_role: str

    observation_type: str

    statement: str

    rating: Optional[int] = None


class ReviewStatementResponse(
    BaseModel
):
    id: int

    workspace_id: int

    claim_schema_id: int

    reviewer_name: str

    reviewer_organization: Optional[
        str
    ]

    reviewer_role: str

    observation_type: str

    statement: str

    rating: Optional[int]

    review_direction: str = "NEUTRAL"

    status: str

    class Config:
        from_attributes = True