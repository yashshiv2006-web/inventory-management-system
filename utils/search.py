"""
Search & Filter Helper Utility.

Purpose:
Provides case-insensitive multi-attribute filtering across product collections.

Why this file exists:
Isolates string matching and query parsing algorithms for educational clarity,
enabling easy testing and reuse across API routes and web controllers.
"""

from typing import List, Any


def filter_by_keyword(items: List[Any], keyword: str, attributes: List[str]) -> List[Any]:
    """
    Filters a list of objects or dictionaries matching a keyword across multiple attributes.

    Args:
        items (List[Any]): Collection to filter.
        keyword (str): Search term.
        attributes (List[str]): List of attribute names to search.

    Returns:
        List[Any]: Matching subset.
    """
    clean_kw = str(keyword).strip().lower()
    if not clean_kw:
        return items

    matched = []
    for item in items:
        for attr in attributes:
            val = getattr(item, attr, None) if hasattr(item, attr) else item.get(attr)
            if val and clean_kw in str(val).lower():
                matched.append(item)
                break

    return matched
