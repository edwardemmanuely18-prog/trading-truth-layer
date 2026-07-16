from __future__ import annotations

from collections import defaultdict

from .models import (
    ExecutionSequence,
    ExecutionState,
    ExecutionStatus,
)


class ExecutionStateBuilder:

    """
    Canonical Execution Builder.

    Converts raw Trade models into
    institutional execution objects.

    Every IIS engine consumes these
    execution states instead of Trade.
    """

    @staticmethod
    def build(

        trades,

    ) -> ExecutionSequence:

        executions: list[
            ExecutionState
        ] = []

        duplicate_counter = defaultdict(int)

        duplicate_tickets: list[str] = []

        missing_open: list[str] = []

        missing_close: list[str] = []

        orphan_positions: list[str] = []

        out_of_order: list[str] = []

        for trade in trades:

            ticket = getattr(
                trade,
                "ticket",
                None,
            )

            if ticket:

                duplicate_counter[
                    ticket
                ] += 1

            opened_at = getattr(
                trade,
                "opened_at",
                None,
            )

            closed_at = getattr(
                trade,
                "closed_at",
                None,
            )

            if opened_at is None:

                missing_open.append(
                    str(ticket)
                )

            if closed_at is None:

                missing_close.append(
                    str(ticket)
                )

            if (

                opened_at
                and
                closed_at
                and
                closed_at < opened_at

            ):

                out_of_order.append(
                    str(ticket)
                )

            status = ExecutionStatus.UNKNOWN

            if closed_at:

                status = ExecutionStatus.CLOSED

            elif opened_at:

                status = ExecutionStatus.OPEN

            executions.append(

                ExecutionState(

                    workspace_id=getattr(
                        trade,
                        "workspace_id",
                        0,
                    ),

                    trade_id=getattr(
                        trade,
                        "id",
                        None,
                    ),

                    broker_connection_id=getattr(
                        trade,
                        "broker_connection_id",
                        None,
                    ),

                    account_id=getattr(
                        trade,
                        "account_id",
                        None,
                    ),

                    symbol=getattr(
                        trade,
                        "symbol",
                        "",
                    ),

                    side=getattr(
                        trade,
                        "side",
                        "",
                    ),

                    ticket=ticket,

                    status=status,

                    opened_at=opened_at,

                    closed_at=closed_at,

                    entry_price=float(

                        getattr(
                            trade,
                            "entry_price",
                            None,
                        ) or 0.0

                    ),

                    exit_price=getattr(
                        trade,
                        "exit_price",
                        None,
                    ),

                    quantity=float(

                        getattr(
                            trade,
                            "quantity",
                            None,
                        ) or 0.0

                    ),

                    realized_pnl=float(

                        getattr(
                            trade,
                            "net_pnl",
                            None,
                        ) or 0.0

                    ),

                    floating_pnl=float(

                        getattr(
                            trade,
                            "floating_pnl",
                            None,
                        ) or 0.0

                    ),

                    commission=float(

                        getattr(
                            trade,
                            "commission",
                            None,
                        ) or 0.0

                    ),

                    swap=float(

                        getattr(
                            trade,
                            "swap",
                            None,
                        ) or 0.0

                    ),

                    fingerprint=getattr(
                        trade,
                        "trade_hash",
                        None,
                    ),

                    metadata={

                        "sync_job_id": getattr(
                            trade,
                            "sync_job_id",
                            None,
                        ),

                        "source_system": getattr(
                            trade,
                            "source_system",
                            None,
                        ),

                        "created_at": getattr(
                            trade,
                            "created_at",
                            None,
                        ),

                        "updated_at": getattr(
                            trade,
                            "updated_at",
                            None,
                        ),

                    },

                )

            )

        for ticket, count in duplicate_counter.items():

            if count > 1:

                duplicate_tickets.append(
                    ticket
                )

        executions.sort(

            key=lambda e: (

                e.opened_at
                or
                e.closed_at,

            )

        )

        return ExecutionSequence(

            executions=executions,

            duplicate_tickets=duplicate_tickets,

            missing_open_times=missing_open,

            missing_close_times=missing_close,

            orphan_positions=orphan_positions,

            out_of_order=out_of_order,

        )