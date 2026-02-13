# zephyrpy/utils/converters.py
CONVERTERS = {
    "str": str,
    "int": int,
    "float": float,
}

def parse_path(path: str):
    segments = []
    kwargs = []
    parts = path.strip("/").split("/")
    for part in parts:
        if part.startswith("{") and part.endswith("}"):
            name_type = part[1:-1]
            if ":" in name_type:
                name, typ = name_type.split(":")
                converter = CONVERTERS.get(typ, str)
            else:
                name, converter = name_type, str
            segments.append(None)
            kwargs.append((name, converter))
        else:
            segments.append(part)
            kwargs.append(None)
    return segments, kwargs