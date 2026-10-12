class AdNotFoundError(Exception):
    pass


class AdSourceUnavailableError(Exception):
    """Temporary error fetching ad data (5xx, network issues)."""

    pass
