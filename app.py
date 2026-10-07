"""Coffee Journal API built with Pixeltable.

    pxt schema update app.py coffee
    pxt service run app.py coffee
"""
import pixeltable as pxt
import pixeltable.functions as pxtf
from pixeltable.serving import FastAPIRouter

from udfs import brew_blurb, roast_label

# ---- tables ----
TableModel = pxt.model_base()


class Cups(TableModel, name='cups'):
    id = pxt.Column(value=pxtf.uuid.uuid7(), primary_key=True)
    bean: pxt.String
    origin: pxt.String
    roast_level: pxt.String | None
    rating: pxt.Int | None
    notes: pxt.String | None

    roast = roast_label(roast_level)
    bean_upper = pxtf.string.upper(bean)
    notes_blurb = brew_blurb(notes)


# ---- queries ----
@pxt.query
def top_cups(origin: str, min_rating: int):
    """Best cups from one origin."""
    return Cups.where((Cups.origin == origin) & (Cups.rating >= min_rating)).select(
        Cups.id, Cups.bean, Cups.roast, Cups.rating, Cups.notes_blurb
    ).order_by(Cups.rating, asc=False)


# ---- routes ----
cups_api = FastAPIRouter(name='cups_api')
cups_api.add_insert_route(
    Cups, path='/cups',
    inputs=[Cups.bean, Cups.origin, Cups.roast_level, Cups.rating, Cups.notes],
    outputs=[Cups.id, Cups.roast, Cups.bean_upper, Cups.notes_blurb],
)
cups_api.add_update_route(Cups, path='/cups/update', inputs=[Cups.roast_level, Cups.rating],
                          outputs=[Cups.id, Cups.roast, Cups.rating])
cups_api.add_compute_route(Cups, path='/roast-label', inputs=[Cups.roast_level], outputs=[Cups.roast])
cups_api.add_query_route(path='/cups/top', query=top_cups, method='get')
