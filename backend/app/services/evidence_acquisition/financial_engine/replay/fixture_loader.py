"""
Trading Truth Layer (TTL)

Universal Evidence Adapter (UEA)

Financial Infrastructure Engine

Replay Fixture Loader

Loads canonical Financial Engine replay fixtures.

This component is intentionally provider-independent.

Responsibilities

• Discover fixture files
• Load fixture contents
• Enumerate datasets

It intentionally performs no:

    • Parsing
    • Normalization
    • Translation
    • Validation
    • Synchronization
"""

from __future__ import annotations

from pathlib import Path

from typing import Iterable
from typing import List
from typing import Optional


# ============================================================================
# Fixture Loader
# ============================================================================


class FixtureLoader:
    """
    Canonical replay fixture loader.

    Provides filesystem access to Financial Engine replay
    datasets.
    """

    def __init__(
        self,
        root: Path | str,
    ) -> None:

        self.root = Path(root)

    # ------------------------------------------------------------------
    # Directories
    # ------------------------------------------------------------------

    @property
    def exists(
        self,
    ) -> bool:

        return self.root.exists()

    # ------------------------------------------------------------------
    # Discovery
    # ------------------------------------------------------------------

    def datasets(
        self,
    ) -> List[str]:
        """
        Return available replay datasets.
        """

        if not self.exists:

            return []

        return sorted(

            directory.name

            for directory in self.root.iterdir()

            if directory.is_dir()

        )

    def fixtures(
        self,
        dataset: str,
    ) -> List[Path]:
        """
        Return every fixture contained within a dataset.

        The search is recursive so datasets may contain
        subdirectories such as:

            valid/
            invalid/
            malformed/
            edge_cases/
        """

        directory = self.root / dataset

        if not directory.exists():

            return []

        return sorted(

            path

            for path in directory.rglob("*")

            if path.is_file()

        )

    # ------------------------------------------------------------------
    # Loading
    # ------------------------------------------------------------------

    def load(
        self,
        dataset: str,
        filename: str,
        encoding: str = "utf-8",
    ) -> str:
        """
        Load a fixture as text.
        """

        path = self.find(filename)

        if path is None:

            raise FileNotFoundError(
                filename,
            )

        return path.read_text(

            encoding=encoding,
        )

    def load_bytes(
        self,
        dataset: str,
        filename: str,
    ) -> bytes:
        """
        Load a fixture as bytes.
        """

        path = self.find(filename)

        if path is None:

            raise FileNotFoundError(
                filename,
            )

        return path.read_bytes()

    # ------------------------------------------------------------------
    # Iteration
    # ------------------------------------------------------------------

    def iterate(
        self,
        dataset: str,
        encoding: str = "utf-8",
    ) -> Iterable[str]:
        """
        Iterate through every fixture contained
        within a dataset.
        """

        for fixture in self.fixtures(

            dataset,

        ):

            yield fixture.read_text(

                encoding=encoding,

            )

    # ------------------------------------------------------------------
    # Lookup
    # ------------------------------------------------------------------

    def find(
        self,
        filename: str,
    ) -> Optional[Path]:
        """
        Locate a fixture by filename.
        """

        if not self.exists:

            return None

        for path in self.root.rglob(filename):

            if path.is_file():

                return path

        return None


# ============================================================================
# Public Exports
# ============================================================================

__all__ = [
    "FixtureLoader",
]