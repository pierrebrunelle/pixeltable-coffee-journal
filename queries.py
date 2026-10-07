"""Queries over the cups table."""
import pixeltable as pxt

from models import Cups


@pxt.query
def top_cups(origin: str, min_rating: int):
    """Best cups from one origin."""
    return Cups.where((Cups.origin == origin) & (Cups.rating >= min_rating)).select(
        Cups.id, Cups.bean, Cups.roast, Cups.rating, Cups.notes_blurb
    ).order_by(Cups.rating, asc=False)
