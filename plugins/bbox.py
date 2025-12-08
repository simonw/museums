from datasette import hookimpl, Response
import json


async def bbox_json(request, datasette):
    """
    Return museums within a bounding box as JSON.

    Query parameters:
    - south: Southern latitude boundary
    - west: Western longitude boundary
    - north: Northern latitude boundary
    - east: Eastern longitude boundary
    """
    try:
        south = float(request.args.get("south", -90))
        west = float(request.args.get("west", -180))
        north = float(request.args.get("north", 90))
        east = float(request.args.get("east", 180))
    except (ValueError, TypeError):
        return Response.json(
            {"error": "Invalid bounding box parameters"},
            status=400
        )

    db = datasette.get_database("browse")

    # Query museums within the bounding box
    sql = """
        SELECT id, name, latitude, longitude
        FROM museums
        WHERE latitude >= :south
          AND latitude <= :north
          AND longitude >= :west
          AND longitude <= :east
          AND permanently_closed IS NULL
        ORDER BY id
    """

    result = await db.execute(
        sql,
        {"south": south, "west": west, "north": north, "east": east}
    )

    museums = [
        {
            "id": row["id"],
            "name": row["name"],
            "latitude": row["latitude"],
            "longitude": row["longitude"]
        }
        for row in result.rows
    ]

    return Response.json(museums)


@hookimpl
def register_routes():
    return [
        (r"^/bbox\.json$", bbox_json),
    ]
