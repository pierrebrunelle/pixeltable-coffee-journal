"""Pixeltable UDFs for the coffee journal (recorded by module path, e.g. `udfs.roast_label`)."""
import pixeltable as pxt

_ROASTS = {'light': 'light', 'cinnamon': 'light', 'city': 'medium', 'city+': 'medium', 'medium': 'medium',
           'full city': 'dark', 'dark': 'dark', 'french': 'dark', 'italian': 'dark'}


@pxt.udf
def roast_label(roast_level: str | None) -> str:
    """Normalize free-form roast names to light / medium / dark."""
    return _ROASTS.get((roast_level or '').strip().lower(), 'unknown')


@pxt.udf
def brew_blurb(notes: str | None) -> str:
    """First tasting note (notes are separated by ';')."""
    first = (notes or '').split(';')[0].strip()
    return first[:40] if first else '-'
