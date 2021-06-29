from typing import Tuple, List, Optional


def parse_stop_description(s: str) -> List[Optional[str]]:
    parts = s.split(':')
    values = []
    for value in parts[1:-1]:
        value = value.rsplit(' ', maxsplit=1)[0].strip()
        if value:
            values.append(value)
        else:
            values.append(None)
    values.append(parts[-1].strip() or None)

    return values


def parse_route_long_name(s: str) -> Tuple[str, str, str, str]:
    from_, to = s.split('<->')
    *from_stop_name, from_city = from_.split('-')
    from_stop_name = ' - '.join(from_stop_name)

    to_stop_name, to_city = to.split('-')[:2]

    return from_stop_name, from_city, to_stop_name, to_city
