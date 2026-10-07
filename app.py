"""Coffee Journal API built with Pixeltable.

    pxt schema update app.py coffee
    pxt service run app.py coffee
"""
from pixeltable.serving import FastAPIRouter

from models import Cups, TableModel  # noqa: F401  (TableModel lets `pxt schema` find the models)
from queries import top_cups

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
