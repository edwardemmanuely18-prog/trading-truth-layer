from __future__ import annotations

"""
Trading Truth Layer
Institutional Chart Framework

Canonical chart builders shared by every
institutional report.

Reports should never construct charts directly.

Supported:

• Horizontal Bar
• Vertical Bar
• Progress Indicator
• Score Bar
• Severity Distribution
• Domain Confidence
• Timeline Density
"""

from reportlab.graphics.charts.barcharts import VerticalBarChart
from reportlab.graphics.charts.barcharts import HorizontalBarChart
from reportlab.graphics.shapes import Drawing
from reportlab.graphics.shapes import String
from reportlab.lib import colors

from .institutional_theme import (
    TTL_NAVY,
    TTL_BLUE,
    TTL_GREEN,
    TTL_RED,
    TTL_AMBER,
)


# ==========================================================
# BAR CHART
# ==========================================================

def build_bar_chart(
    *,
    labels: list[str],
    values: list[float],
    title: str,
    width: int = 420,
    height: int = 180,
):

    drawing = Drawing(
        width,
        height + 30,
    )

    drawing.add(

        String(

            0,
            height + 10,

            title,

            fontName="Helvetica-Bold",

            fontSize=11,

        )

    )

    chart = VerticalBarChart()

    chart.x = 35

    chart.y = 25

    chart.width = width - 60

    chart.height = height - 35

    chart.data = [values]

    chart.categoryAxis.categoryNames = labels

    chart.valueAxis.valueMin = 0

    chart.valueAxis.valueMax = max(
        values + [100],
    )

    chart.valueAxis.valueStep = max(
        10,
        int(chart.valueAxis.valueMax / 5),
    )

    chart.bars[0].fillColor = TTL_BLUE

    drawing.add(chart)

    return drawing


# ==========================================================
# HORIZONTAL BAR
# ==========================================================

def build_horizontal_bar_chart(
    *,
    labels: list[str],
    values: list[float],
    title: str,
    width: int = 420,
    height: int = 180,
):

    drawing = Drawing(
        width,
        height + 30,
    )

    drawing.add(

        String(

            0,
            height + 10,

            title,

            fontName="Helvetica-Bold",

            fontSize=11,

        )

    )

    chart = HorizontalBarChart()

    chart.x = 90

    chart.y = 20

    chart.width = width - 110

    chart.height = height - 40

    chart.data = [values]

    chart.categoryAxis.categoryNames = labels

    chart.valueAxis.valueMin = 0

    chart.valueAxis.valueMax = max(
        values + [100],
    )

    chart.bars[0].fillColor = TTL_GREEN

    drawing.add(chart)

    return drawing


# ==========================================================
# SCORE BAR
# ==========================================================

def score_colour(
    score: float,
):

    if score >= 85:
        return TTL_GREEN

    if score >= 70:
        return TTL_BLUE

    if score >= 50:
        return TTL_AMBER

    return TTL_RED


def build_score_bar(
    score: float,
    width: int = 260,
):

    drawing = Drawing(
        width,
        28,
    )

    drawing.add(

        String(

            0,

            16,

            f"Score {score:.2f}",

            fontName="Helvetica-Bold",

            fontSize=10,

        )

    )

    colour = score_colour(score)

    drawing.add(

        colors.Line(
            0,
            5,
            width,
            5,
        )

    )

    return drawing


# ==========================================================
# DOMAIN CONFIDENCE
# ==========================================================

def build_domain_confidence_chart(
    domains: dict[str, float],
):

    return build_horizontal_bar_chart(

        labels=list(domains.keys()),

        values=list(domains.values()),

        title="Investigation Domain Confidence",

    )


# ==========================================================
# SEVERITY DISTRIBUTION
# ==========================================================

def build_severity_chart(
    severities: dict[str, int],
):

    return build_bar_chart(

        labels=list(severities.keys()),

        values=list(severities.values()),

        title="Finding Severity Distribution",

    )


__all__ = [

    "build_bar_chart",

    "build_horizontal_bar_chart",

    "build_score_bar",

    "build_domain_confidence_chart",

    "build_severity_chart",

]