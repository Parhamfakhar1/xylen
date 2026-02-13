# Xylen/router.py
from .utils.converters import parse_path

class Route:
    def __init__(self, path, handler, methods):
        self.segments, self.kwargs = parse_path(path)
        self.handler = handler
        self.methods = [m.upper() for m in methods]

class Router:
    def __init__(self):
        self.routes = []

    def add_route(self, path, handler, methods):
        self.routes.append(Route(path, handler, methods))

    def resolve(self, path: str, method: str):
        clean_path = path.strip("/")
        path_parts = clean_path.split("/") if clean_path else []

        for route in self.routes:
            if method not in route.methods:
                continue
            if len(path_parts) != len(route.segments):
                continue

            kwargs = {}
            match = True
            for i, seg in enumerate(route.segments):
                expected = seg
                actual = path_parts[i]
                kw = route.kwargs[i]

                if expected is None:  # dynamic segment
                    name, converter = kw
                    try:
                        kwargs[name] = converter(actual)
                    except (ValueError, TypeError):
                        match = False
                        break
                else:
                    if expected != actual:
                        match = False
                        break

            if match:
                return route.handler, kwargs

        return None, {}