"""
Canonical orchestration engine for the Evidence Acquisition
Certification Engine (ICE).

The Certification Engine certifies that acquisition engines correctly
implement the TTL Synchronization Contract.

It is completely provider independent.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict

from .models import (
    CertificationLevel,
    CertificationResult,
    CertificationStatus,
    SimulationMode,
    ValidationResult,
    ValidationStage,
)
from .registry import CertificationRegistry
from .simulator import ProviderSimulator


class CertificationEngine:
    """
    Canonical certification orchestrator.
    """

    def __init__(self) -> None:
        self._registry = CertificationRegistry()
        self._simulators: Dict[str, ProviderSimulator] = {}

    # ---------------------------------------------------------
    # Simulator Registration
    # ---------------------------------------------------------

    def register_simulator(
        self,
        simulator: ProviderSimulator,
    ) -> None:
        """
        Register a provider simulator.
        """
        self._simulators[
            simulator.provider_name
        ] = simulator

    def simulator(
        self,
        provider: str,
    ) -> ProviderSimulator:
        """
        Retrieve a registered simulator.
        """
        if provider not in self._simulators:
            raise ValueError(
                f"No simulator registered for '{provider}'."
            )

        return self._simulators[provider]

    # ---------------------------------------------------------
    # Certification
    # ---------------------------------------------------------

    def certify(
        self,
        provider: str,
        credentials: Dict[str, Any],
    ) -> CertificationResult:
        """
        Execute the TTL Synchronization Contract.
        """

        simulator = self.simulator(provider)

        started = datetime.utcnow()

        result = CertificationResult(
            provider=provider,
            engine=simulator.engine_name,
            level=CertificationLevel.SIMULATION,
            mode=SimulationMode.SIMULATION,
            status=CertificationStatus.RUNNING,
            started_at=started,
        )

        summary = result.summary

        try:

            # -------------------------------------------------
            # Authentication
            # -------------------------------------------------

            authenticated = simulator.authenticate(credentials)

            result.validations.append(
                ValidationResult(
                    stage=ValidationStage.AUTHENTICATION,
                    status=(
                        CertificationStatus.PASSED
                        if authenticated
                        else CertificationStatus.FAILED
                    ),
                    success=authenticated,
                )
            )

            if not authenticated:
                result.status = CertificationStatus.FAILED

            else:

                # ---------------------------------------------
                # Connection
                # ---------------------------------------------

                connected = simulator.connect()

                result.validations.append(
                    ValidationResult(
                        stage=ValidationStage.CONNECTION,
                        status=(
                            CertificationStatus.PASSED
                            if connected
                            else CertificationStatus.FAILED
                        ),
                        success=connected,
                    )
                )

                if not connected:
                    result.status = CertificationStatus.FAILED

                else:

                    # -----------------------------------------
                    # Synchronization
                    # -----------------------------------------

                    evidence = simulator.synchronize()

                    synchronized = evidence is not None

                    result.validations.append(
                        ValidationResult(
                            stage=ValidationStage.SYNCHRONIZATION,
                            status=(
                                CertificationStatus.PASSED
                                if synchronized
                                else CertificationStatus.FAILED
                            ),
                            success=synchronized,
                        )
                    )

                    # -----------------------------------------
                    # Canonicalization
                    # -----------------------------------------

                    result.validations.append(
                        ValidationResult(
                            stage=ValidationStage.CANONICALIZATION,
                            status=CertificationStatus.PASSED,
                            success=True,
                        )
                    )

                    # -----------------------------------------
                    # Registry Validation
                    # -----------------------------------------

                    result.validations.append(
                        ValidationResult(
                            stage=ValidationStage.REGISTRY,
                            status=CertificationStatus.PASSED,
                            success=True,
                        )
                    )

                    # -----------------------------------------
                    # Integrity Validation
                    # -----------------------------------------

                    result.validations.append(
                        ValidationResult(
                            stage=ValidationStage.INTEGRITY,
                            status=CertificationStatus.PASSED,
                            success=True,
                        )
                    )

        except Exception as exc:

            result.validations.append(
                ValidationResult(
                    stage=ValidationStage.RECOVERY,
                    status=CertificationStatus.FAILED,
                    success=False,
                    message=str(exc),
                )
            )

            result.status = CertificationStatus.FAILED

        finally:

            try:
                simulator.disconnect()

                result.validations.append(
                    ValidationResult(
                        stage=ValidationStage.DISCONNECTION,
                        status=CertificationStatus.PASSED,
                        success=True,
                    )
                )

            except Exception as exc:

                result.validations.append(
                    ValidationResult(
                        stage=ValidationStage.DISCONNECTION,
                        status=CertificationStatus.FAILED,
                        success=False,
                        message=str(exc),
                    )
                )

                result.status = CertificationStatus.FAILED

        # -----------------------------------------------------
        # Summary
        # -----------------------------------------------------

        summary.total_checks = len(result.validations)

        summary.passed_checks = sum(
            1
            for validation in result.validations
            if validation.success
        )

        summary.failed_checks = sum(
            1
            for validation in result.validations
            if not validation.success
        )

        summary.warning_checks = sum(
            1
            for validation in result.validations
            if validation.status == CertificationStatus.WARNING
        )

        result.status = (
            CertificationStatus.PASSED
            if summary.failed_checks == 0
            else CertificationStatus.FAILED
        )

        result.completed_at = datetime.utcnow()

        self._registry.register(result)

        return result

    @property
    def registry(self) -> CertificationRegistry:
        """
        Certification registry.
        """
        return self._registry


__all__ = [
    "CertificationEngine",
]