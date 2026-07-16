from __future__ import annotations

from .models import (
    ExecutionIntegrity,
    ExecutionSequence,
    IntegrityLevel,
)


# ============================================================
# Institutional Execution Integrity Engine
# ============================================================

class ExecutionIntegrityEngine:

    """
    Performs institutional integrity validation
    against the canonical execution sequence.

    This engine NEVER queries the database.

    Input:
        ExecutionSequence

    Output:
        ExecutionIntegrity
    """

    @staticmethod
    def evaluate(

        sequence: ExecutionSequence,

    ) -> ExecutionIntegrity:

        findings: list[str] = []

        score = 100.0

        duplicate_count = len(
            sequence.duplicate_tickets
        )

        orphan_count = len(
            sequence.orphan_positions
        )

        timestamp_count = (

            len(sequence.missing_open_times)

            +

            len(sequence.missing_close_times)

        )

        ordering_count = len(
            sequence.out_of_order
        )

        # =====================================================
        # Duplicate Executions
        # =====================================================

        if duplicate_count:

            findings.append(

                f"{duplicate_count} duplicated execution ticket(s)."

            )

            score -= duplicate_count * 5

        # =====================================================
        # Missing Open Times
        # =====================================================

        if sequence.missing_open_times:

            findings.append(

                f"{len(sequence.missing_open_times)} execution(s) missing open timestamp."

            )

            score -= (

                len(sequence.missing_open_times)

                * 2

            )

        # =====================================================
        # Missing Close Times
        # =====================================================

        if sequence.missing_close_times:

            findings.append(

                f"{len(sequence.missing_close_times)} execution(s) still open."

            )

            score -= (

                len(sequence.missing_close_times)

            )

        # =====================================================
        # Orphan Positions
        # =====================================================

        if orphan_count:

            findings.append(

                f"{orphan_count} orphan execution(s)."

            )

            score -= orphan_count * 4

        # =====================================================
        # Invalid Ordering
        # =====================================================

        if ordering_count:

            findings.append(

                f"{ordering_count} execution(s) contain invalid chronology."

            )

            score -= ordering_count * 5

        # =====================================================
        # Invalid Prices
        # =====================================================

        invalid_prices = [

            execution

            for execution in sequence.executions

            if (

                execution.entry_price <= 0

                or

                (

                    execution.exit_price is not None

                    and

                    execution.exit_price <= 0

                )

            )

        ]

        if invalid_prices:

            findings.append(

                f"{len(invalid_prices)} execution(s) contain invalid pricing."

            )

            score -= len(
                invalid_prices
            ) * 3

        # =====================================================
        # Invalid Quantity
        # =====================================================

        invalid_volume = [

            execution

            for execution in sequence.executions

            if execution.quantity <= 0

        ]

        if invalid_volume:

            findings.append(

                f"{len(invalid_volume)} execution(s) contain invalid quantity."

            )

            score -= len(
                invalid_volume
            ) * 3

        # =====================================================
        # Clamp
        # =====================================================

        score = max(

            0.0,

            min(

                100.0,

                score,

            ),

        )

        # =====================================================
        # Integrity Level
        # =====================================================

        if score >= 95:

            level = IntegrityLevel.VERIFIED

        elif score >= 80:

            level = IntegrityLevel.WARNING

        else:

            level = IntegrityLevel.FAILED

        return ExecutionIntegrity(

            level=level,

            score=round(
                score,
                2,
            ),

            duplicate_count=duplicate_count,

            orphan_count=orphan_count,

            missing_timestamp_count=timestamp_count,

            findings=findings,

        )