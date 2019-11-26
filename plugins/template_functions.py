from datasette import hookimpl
import datetime
import json


@hookimpl
def extra_template_vars():
    return {
        "json": json,
        "nicer_date": lambda d: datetime.datetime.strptime(d, "%d-%M-%Y").strftime(
            "%e %B %Y"
        ),
    }
