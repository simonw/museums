from datasette import hookimpl
import datetime
import json


def pluralize(number, singular="", plural="s"):
    if number == 1:
        return singular
    else:
        return plural


@hookimpl
def extra_template_vars():
    return {
        "json": json,
        "nicer_date": lambda d: "{dt.day} {dt:%B} {dt.year}".format(
            dt=datetime.datetime.strptime(d.split("T")[0], "%Y-%m-%d")
        )
        if d is not None
        else "",
        "pluralize": pluralize,
    }
