from datasette import hookimpl
from datasette.utils.asgi import Response

ROBOTS_TXT = """
Sitemap: https://www.niche-museums.com/sitemap.xml

User-agent: *
Disallow: /browse
""".strip()


@hookimpl
def register_routes():
    return [
        ("^/robots.txt$", robots_txt),
        ("^/sitemap.xml$", sitemap_xml),
    ]


def robots_txt():
    return Response.text(ROBOTS_TXT)


async def sitemap_xml(datasette):
    content = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
    ]
    db = datasette.get_database("browse")
    for row in await db.execute("select id from museums order by id desc"):
        content.append(
            "<url><loc>https://www.niche-museums.com/{}</loc></url>".format(row["id"])
        )
    content.append("</urlset>")
    return Response("\n".join(content), 200, content_type="application/xml")
