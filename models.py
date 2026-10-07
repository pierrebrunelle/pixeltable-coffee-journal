"""The cups table."""
import pixeltable as pxt
import pixeltable.functions as pxtf

from udfs import brew_blurb, roast_label

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
