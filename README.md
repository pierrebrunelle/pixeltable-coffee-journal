<!-- pixeltable-example-app: 20260925-coffee-journal -->
# Coffee Journal API built with Pixeltable

[![Built with Pixeltable](https://img.shields.io/badge/built%20with-Pixeltable-5b4bff)](https://pixeltable.com)
[![PyPI - pixeltable](https://img.shields.io/pypi/v/pixeltable?label=pixeltable)](https://pypi.org/project/pixeltable/)
[![GitHub stars](https://img.shields.io/github/stars/pixeltable/pixeltable?style=social)](https://github.com/pixeltable/pixeltable)
[![License: Apache-2.0](https://img.shields.io/badge/license-Apache--2.0-blue)](LICENSE)

Log every cup: bean, origin, roast level, a 1-5 rating and free-form tasting notes. Pixeltable normalizes the roast into a label, upper-cases the bean for display and condenses the notes into a one-line summary, all as **computed columns**. A query returns your best-rated cups from one origin, and the whole thing is a typed FastAPI service you can run locally or on **Pixeltable Cloud**.

[Pixeltable](https://pixeltable.com) is open-source, Python-native **multimodal AI data infrastructure**: tables, incremental computed columns, UDFs, indexes and serving in one library, running locally or on Pixeltable Cloud.

> ⭐ **Like this example?** Star [pixeltable/pixeltable](https://github.com/pixeltable/pixeltable) on GitHub. It helps other developers find it.

## What this example shows

- **FastAPI serving**: one `FastAPIRouter` turns tables and `@pxt.query` functions into typed REST routes (insert, update, delete, compute and query) with OpenAPI docs
- **Pixeltable Cloud lifecycle** from the `pxt` CLI (`db`, `schema`, `service`)
- **Incremental computed columns** powered by plain Python UDFs (`@pxt.udf`)
- **Importable UDF module**: UDFs in `udfs.py`, tables in `models.py`, queries in `queries.py`, routes in `app.py` (Pixeltable resolves UDFs by module path)
- **`pixeltable.toml`** declares a local database and a **Pixeltable Cloud** database, so the same code deploys with `pxt db update`

## Data model at a glance

| You send | Pixeltable stores and computes |
|----------|-------------------------------|
| `roast_level` (`"light"`, `"City+"`, `"french"` ...) | `roast_label`: one of `light`, `medium`, `dark`, `unknown` |
| `bean` | `bean_upper` |
| `notes` | `notes_blurb`: the first tasting note, trimmed |

Because these are columns rather than view logic, they're queryable: `top_cups` filters on `rating` and sorts by it inside Pixeltable.

## What's inside

| File | What it is |
|------|------------|
| `app.py` | The API: one `FastAPIRouter` wiring the tables and queries into REST routes |
| `client_demo.py` | Log a cup, adjust it and query top-rated coffees through the API |
| `models.py` | Tables declared as Python classes: columns, computed columns, indexes |
| `pixeltable.toml` | Project config: the local database plus a Pixeltable Cloud database (sizing, deploy excludes) |
| `queries.py` | `@pxt.query` functions served as query routes |
| `seed.py` | Seed a few cups of coffee |
| `udfs.py` | Pixeltable UDFs (`@pxt.udf`) in their own importable module |
| `requirements.txt` / `pyproject.toml` | Dependencies (`pixeltable[serve]>=0.7.14`) |

**Tables**

| Table | Stored columns | Computed columns |
|-------|---------|------------------|
| `cups` | `bean`, `origin`, `roast_level`, `rating`, `notes` | `id`, `roast`, `bean_upper`, `notes_blurb` |

**API routes** (service `cups_api`)

| Method | Path | Kind | Backed by | Notes |
|--------|------|------|-----------|-------|
| `POST` | `/cups` | insert | `Cups` |  |
| `POST` | `/cups/update` | update | `Cups` |  |
| `POST` | `/roast-label` | compute | `Cups` |  |
| `GET` | `/cups/top` | query | `top_cups` |  |

## Quickstart

Requires Python 3.11+ and `pixeltable[serve]>=0.7.14`.

```bash
git clone https://github.com/pierrebrunelle/pixeltable-coffee-journal.git
cd pixeltable-coffee-journal
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# Create the tables in a local catalog directory named `coffee`
pxt schema update app.py coffee

python seed.py coffee
pxt service run app.py coffee --port 8000   # open http://localhost:8000/docs
python client_demo.py                      # in another terminal
```

Try it:

```bash
curl -s -X POST localhost:8000/roast-label -H 'Content-Type: application/json' -d '{"roast_level": "Full City"}'
curl -s 'localhost:8000/cups/top?origin=Ethiopia&min_rating=4'
```

## Deploy to Pixeltable Cloud

The same `app.py` runs on [Pixeltable Cloud](https://pixeltable.com). Sign in (or get a free trial database with `pxt new`), point the second database entry in `pixeltable.toml` at your own database, then deploy:

```bash
pxt login                       # or: export PIXELTABLE_API_KEY=<your-api-key>
# edit pixeltable.toml: name = 'pxt://<your-org>:<your-db>'
pxt db update pxt://<your-org>:<your-db>                 # build the image and upload the project
pxt schema update app.py pxt://<your-org>:<your-db>/coffee   # create the tables in the hosted database
pxt service update app.py pxt://<your-org>:<your-db>/coffee  # start the API there
pxt service list pxt://<your-org>:<your-db>              # list hosted services
```

Hosted routes require an API key: send it in the `X-api-key` header (for example `-H "X-api-key: $PIXELTABLE_API_KEY"`). Keep keys in environment variables or `pxt secret set`, never in code.

## Code walkthrough

**1. Business logic is plain Python, in `udfs.py`.** A `@pxt.udf` function can be used as a column expression. Pixeltable records UDFs by module path (`udfs.roast_label`), so they live in their own importable module rather than inline in the app: the daemon, serving workers and Pixeltable Cloud import it again by that path.

```python
# udfs.py
@pxt.udf
def roast_label(roast_level: str | None) -> str:
    """Normalize free-form roast names to light / medium / dark."""
    return _ROASTS.get((roast_level or '').strip().lower(), 'unknown')
```

**2. Tables are Python classes (`models.py`).** Annotated attributes are stored columns; attributes assigned an expression are **computed columns** (`id`, `roast`, `bean_upper`, `notes_blurb`), evaluated incrementally on every insert or update and recomputed when their inputs change.

```python
# models.py
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
```

**3. Queries are functions (`queries.py`).** `@pxt.query` wraps a Pixeltable query so it can be called from Python or exposed as a route:

```python
# queries.py
@pxt.query
def top_cups(origin: str, min_rating: int):
    """Best cups from one origin."""
    return Cups.where((Cups.origin == origin) & (Cups.rating >= min_rating)).select(
        Cups.id, Cups.bean, Cups.roast, Cups.rating, Cups.notes_blurb
    ).order_by(Cups.rating, asc=False)
```

**4. One router, a full REST API.** `FastAPIRouter` generates request/response models from the column types, validates input, and publishes OpenAPI docs at `/docs`:

```python
# app.py
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
```

## Learn more

- 🌐 Website: https://pixeltable.com
- 📚 Docs: https://docs.pixeltable.com
- 💻 Source: https://github.com/pixeltable/pixeltable (⭐ star it if Pixeltable is useful to you)
- 📦 PyPI: https://pypi.org/project/pixeltable/

---

<sub>Built as part of a daily series of Pixeltable example apps · Pixeltable 0.7.14 · Python, FastAPI, incremental computed columns · Licensed under Apache-2.0.</sub>
