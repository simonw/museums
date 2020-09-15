from datasette import hookimpl
from datasette.utils.asgi import Response


@hookimpl
def register_routes():
    return [
        ("^/robots.txt$", robots_txt),
        ("^/sitemap.xml$", sitemap_xml),
    ]


def robots_txt():
    return Response.text("Sitemap: https://www.niche-museums.com/sitemap.xml")


async def sitemap_xml(datasette):
    content = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
    ]
    for db in datasette.databases.values():
        for row in await db.execute("select id from museums"):
            content.append(
                "<url><loc>https://www.niche-museums.com/{}</loc></url>".format(
                    row["id"]
                )
            )
    content.append("</urlset>")
    return Response("\n".join(content), 200, content_type="application/xml")
