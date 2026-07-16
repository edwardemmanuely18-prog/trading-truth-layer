from __future__ import annotations

from app.core.page_registry import PAGE_REGISTRY


def get_page_definition(

    page: str,

):

    return PAGE_REGISTRY.get(page)