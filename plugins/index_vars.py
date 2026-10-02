from datasette import hookimpl

PAGE_SIZE = 15


@hookimpl
def extra_template_vars(request, view_name):
    vars = {"q": request.args.get("q") or ""}
    if view_name == "index":
        # Custom template variables for the homepage
        select = "*"
        order_by = f"id desc limit {PAGE_SIZE}"
        where = ""
        next = None
        is_distance_page = False

        if request.args.get("latitude") and request.args.get("longitude"):
            try:
                latitude = float(request.args.get("latitude"))
                longitude = float(request.args.get("longitude"))
            except ValueError:
                latitude = longitude = None
            if latitude is not None and longitude is not None:
                select = f"*, haversine(latitude, longitude, cast({latitude!r} as real), cast({longitude!r} as real), 'mi') as distance_mi"
                order_by = f"distance_mi limit {PAGE_SIZE}"
                is_distance_page = True
                vars.update({"latitude": latitude, "longitude": longitude})

        # Handle ?next= link
        next = request.args.get("next")
        if next and next.isdigit():
            where = f" where id < {next} "

        query = f"select {select} from museums {where} order by {order_by}"

        vars.update(
            {
                "query": query,
                "should_next_query": f"select (count(*) - {PAGE_SIZE}) > 0 from museums {where}",
                "next_query": f"select min(id) from ({query})",
                "is_distance_page": is_distance_page,
            }
        )
    return vars
