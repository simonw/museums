from datasette import hookimpl
from datasette.utils.asgi import asgi_send, Response
from functools import wraps

HOST_REDIRECTS = {
    b"nichemuseums.local": b"www.nichemuseums.local",
    b"niche-museums.com": b"www.niche-museums.com",
}


def redirect_museum(request):
    return Response.redirect("/{}".format(request.url_vars["id"]), status=301)


@hookimpl
def register_routes():
    return [
        (r"^/6$", lambda: Response.redirect("/103", status=301)),
        (r"^/browse/museums/(?P<id>\d+)$", redirect_museum),
    ]


@hookimpl
def asgi_wrapper(datasette):
    def wrap_with_www_redirect(app):
        @wraps(app)
        async def www_redirect(scope, recieve, send):
            if scope.get("method") == "GET":
                host = (dict(scope["headers"]).get(b"host") or b"").split(b":")[0]
                host_no_port = host.split(b":")[0]
                if host_no_port in HOST_REDIRECTS:
                    new_host = HOST_REDIRECTS[host_no_port]
                    # Is there a port to add?
                    if b":" in host:
                        port = host.split(b":")[-1]
                        new_host += b":" + port
                    return await send_host_redirect(scope, send, new_host)
            await app(scope, recieve, send)

        return www_redirect

    return wrap_with_www_redirect


async def send_host_redirect(scope, send, new_host, status=301):
    path = scope.get("raw_path") or scope.get("path", "").encode("utf8")
    query_string = scope["query_string"]
    if query_string:
        path = path + b"?" + query_string
    new_url = b"https://" + new_host + path
    await send(
        {
            "type": "http.response.start",
            "status": status,
            "headers": [[b"location", new_url]],
        }
    )
    await send({"type": "http.response.body", "body": b""})
