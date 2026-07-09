from __future__ import annotations

from threading import RLock

from app.models.workspace import Workspace


# ============================================================
# INTERNAL PLAN SIMULATION
# ============================================================
#
# PURPOSE
#
# This service allows internal developers to simulate
# different commercial plans WITHOUT modifying:
#
# - Workspace.plan_code
# - Billing provider
# - Subscription records
# - Paddle
# - Stripe
#
# The simulation only affects entitlement resolution.
#
# ============================================================


class PlanSimulationService:

    _lock = RLock()

    #
    # workspace_id -> simulated_plan
    #
    _overrides: dict[int, str] = {}

    # --------------------------------------------------------
    # Read
    # --------------------------------------------------------

    @classmethod
    def get_override(
        cls,
        workspace_id: int,
    ) -> str | None:

        with cls._lock:

            return cls._overrides.get(
                workspace_id,
            )

    # --------------------------------------------------------
    # Write
    # --------------------------------------------------------

    @classmethod
    def set_override(
        cls,
        workspace_id: int,
        plan: str,
    ) -> None:

        with cls._lock:

            cls._overrides[
                workspace_id
            ] = plan

    # --------------------------------------------------------
    # Remove
    # --------------------------------------------------------

    @classmethod
    def clear_override(
        cls,
        workspace_id: int,
    ) -> None:

        with cls._lock:

            cls._overrides.pop(
                workspace_id,
                None,
            )

    # --------------------------------------------------------
    # Status
    # --------------------------------------------------------

    @classmethod
    def simulation_enabled(
        cls,
        workspace_id: int,
    ) -> bool:

        return (
            cls.get_override(
                workspace_id,
            )
            is not None
        )

    # --------------------------------------------------------
    # Effective Plan
    # --------------------------------------------------------

    @classmethod
    def effective_plan(
        cls,
        workspace: Workspace,
    ) -> str:

        override = cls.get_override(
            workspace.id,
        )

        if override:

            return override

        #
        # Billing remains canonical.
        #

        return workspace.plan_code

    # --------------------------------------------------------
    # Snapshot
    # --------------------------------------------------------

    @classmethod
    def build_snapshot(
        cls,
        workspace: Workspace,
    ) -> dict:

        return {

            "workspace_id":
                workspace.id,

            "actual_plan":
                workspace.plan_code,

            "effective_plan":
                cls.effective_plan(
                    workspace,
                ),

            "simulation_enabled":
                cls.simulation_enabled(
                    workspace.id,
                ),

            "simulated_plan":
                cls.get_override(
                    workspace.id,
                ),

        }