from datasette import hookimpl, Response


async def museums_json(request, datasette):
    db = datasette.get_database("browse")
    result = await db.execute(
        """
        select
            name,
            'https://www.niche-museums.com/' || id as url,
            address,
            description,
            photo_url,
            photo_alt,
            created
        from
            museums
        order by
            id
        """
    )
    museums = [dict(row) for row in result.rows]
    return Response.json(museums)


@hookimpl
def register_routes():
    return [
        (r"^/museums\.json$", museums_json),
    ]
