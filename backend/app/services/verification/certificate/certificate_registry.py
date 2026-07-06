from __future__ import annotations

from app.services.verification.certificate.certificate_models import (
    VerificationCertificate,
)


class CertificateRegistry:

    def __init__(self):

        self._certificates = {}

    def store(
        self,
        certificate: VerificationCertificate,
    ):

        self._certificates[
            certificate.identity.claim_schema_id
        ] = certificate

    def get(
        self,
        claim_schema_id: int,
    ):

        return self._certificates.get(
            claim_schema_id
        )

    def exists(
        self,
        claim_schema_id: int,
    ):

        return (
            claim_schema_id
            in self._certificates
        )

    def clear(self):

        self._certificates.clear()


certificate_registry = CertificateRegistry()