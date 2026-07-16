@dataclass(frozen=True)
class AccessContext:

    workspace_id: int

    user_id: int

    role: str

    plan: str

    billing_status: str