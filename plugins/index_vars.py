from datasette import hookimpl

PAGE_SIZE = 15


@hookimpl
def extra_template_vars(request, view_name):
    vars = {"q": request.raw_args.get("q") or ""}
    if view_name == "index":
        # Custom template variables for the homepage
        args = request.raw_args
        select = "*"
        order_by = f"id desc limit {PAGE_SIZE}"
        where = ""
        next = None
        is_distance_page = False

        if args.get("latitude") and args.get("longitude"):
            select = f"*, haversine(latitude, longitude, cast({args['latitude']} as real), cast({args['longitude']} as real), 'mi') as distance_mi"
            order_by = f"distance_mi limit {PAGE_SIZE}"
            is_distance_page = True
            vars.update(
                {
                    "latitude": float(args["latitude"]),
                    "longitude": float(args["longitude"]),
                }
            )

        # Handle ?next= link
        next = args.get("next")
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
