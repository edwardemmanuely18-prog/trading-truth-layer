"""
Trading Truth Layer (TTL)

SWIFT FIN Field Parser

Parses Block 4 business fields.
"""

from __future__ import annotations

import re

from dataclasses import dataclass
from dataclasses import field

from typing import Dict


FIELD_PATTERN = re.compile(
    r"^:(\d{2}[A-Z]?):(.*)$"
)


@dataclass(slots=True)
class FINField:

    tag: str

    value: str


@dataclass(slots=True)
class FINFieldCollection:

    fields: Dict[str, FINField] = field(
        default_factory=dict
    )

    def __contains__(
        self,
        tag: str,
    ) -> bool:

        return tag in self.fields


    def __len__(
        self,
    ) -> int:

        return len(self.fields)


    def __iter__(
        self,
    ):

        return iter(
            self.fields.values()
        )

    def add(
        self,
        field_value: FINField,
    ) -> None:

        self.fields[
            field_value.tag
        ] = field_value

    def value(
        self,
        tag: str,
    ) -> str | None:

        field = self.fields.get(tag)

        return None if field is None else field.value

    def field(
        self,
        tag: str,
    ) -> FINField | None:

        return self.fields.get(
            tag,
        )

    def require(
        self,
        tag: str,
    ) -> str:

        value = self.value(
            tag,
        )

        if value is None:

            raise KeyError(
                f"Missing FIN field {tag}"
            )

        return value

    def as_dict(
        self,
    ) -> Dict[str, str]:

        return {

            tag: field.value

            for tag, field

            in self.fields.items()

        }


class FINFieldParser:
    """
    Parses Block 4 fields.
    """

    def parse(
        self,
        text: str,
    ) -> FINFieldCollection:

        text = text.strip()

        collection = FINFieldCollection()

        tag = None

        buffer = []

        for raw_line in text.splitlines():

            line = raw_line.rstrip()

            if not line:

                continue

            match = FIELD_PATTERN.match(
                line
            )

            if match:

                if tag is not None:

                    collection.add(

                        FINField(

                            tag=tag,

                            value="\n".join(buffer).strip(),
                        )
                    )

                tag = match.group(1)

                buffer = [match.group(2)]

            else:

                # SWIFT Block 4 terminator ("-") is a transport
                # delimiter, not business data.
                if line.strip() == "-":

                    continue

                buffer.append(
                    line,
                )

        if tag is not None:

            collection.add(

                FINField(

                    tag=tag,

                    value="\n".join(buffer).strip(),
                )
            )

        return collection

    def parse_dict(
        self,
        text: str,
    ) -> Dict[str, str]:

        return self.parse(
            text,
        ).as_dict()

    def supports(
        self,
        text: str,
        tag: str,
    ) -> bool:

        return tag in self.parse(
            text,
        )


__all__ = [

    "FINField",

    "FINFieldCollection",

    "FINFieldParser",
]