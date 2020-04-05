from datasette import hookimpl
from datasette_render_markdown import render_markdown


def escape_fts_query(query):
    bits = query.split()
    return " ".join('"{}"'.format(bit.replace('"', "")) for bit in bits)


@hookimpl
def prepare_connection(conn):
    conn.create_function("render_markdown", 1, render_markdown)
    conn.create_function("escape_fts_query", 1, escape_fts_query)
