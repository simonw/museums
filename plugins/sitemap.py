from datasette import hookimpl
from datasette.utils.asgi import asgi_send
from functools import wraps


@hookimpl
def asgi_wrapper(datasette):
    def wrap_with_robots_and_sitemap(app):
        @wraps(app)
        async def robots_and_sitemap(scope, recieve, send):
            if scope["path"] == "/robots.txt":
                await asgi_send(
                    send, "Sitemap: https://www.niche-museums.com/sitemap.xml", 200
                )
            elif scope["path"] == "/sitemap.xml":
                await send_sitemap(send, datasette)
            else:
                await app(scope, recieve, send)

        return robots_and_sitemap

    return wrap_with_robots_and_sitemap


async def send_sitemap(send, datasette):
    content = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
    ]
    for db in datasette.databases.values():
        hidden = await db.hidden_table_names()
        tables = await db.table_names()
        for table in tables:
            if table in hidden:
                continue
            for row in await db.execute("select id from [{}]".format(table)):
                content.append(
                    "<url><loc>https://www.niche-museums.com/browse/{}/{}</loc></url>".format(
                        table, row["id"]
                    )
                )
    content.append("</urlset>")
    await asgi_send(send, "\n".join(content), 200, content_type="application/xml")
