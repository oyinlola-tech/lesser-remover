"""Shared PDF page-selection parsing."""


def parse_page_selection(spec: str, page_count: int) -> list[int]:
    """Parse a page selection like '1,3-5' into 1-based page numbers."""
    selection: list[int] = []
    for token in spec.split(","):
        token = token.strip()
        if not token:
            continue
        if "-" in token:
            start, end = token.split("-", 1)
            start = int(start.strip())
            end = int(end.strip())
            if start < 1 or end > page_count or start > end:
                raise ValueError(
                    f"Invalid page range: {token}"
                )
            selection.extend(range(start, end + 1))
        else:
            page = int(token)
            if page < 1 or page > page_count:
                raise ValueError(
                    f"Invalid page number: {token}"
                )
            selection.append(page)
    selection = sorted(set(selection))
    if not selection:
        raise ValueError("Page selection is empty.")
    return selection
