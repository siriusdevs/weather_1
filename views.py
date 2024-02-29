from typing import Optional

import config


def load_page(template_path: str, formating: Optional[dict] = None):
    with open(template_path, 'r') as template:
        page = template.read()
    if formating:
        page = page.format(**formating)
    return page


def plusses_to_spaces(text: str) -> str:
    return text.replace('+', ' ')


def spaces_to_plusses(text: str) -> str:
    return text.replace(' ', '+')


def main() -> str:
    return load_page(config.TEMPLATE_MAIN)


def weather(weather_data: dict) -> str:
    return load_page(config.TEMPLATE_WEATHER, weather_data)


def weather_dummy(cities: list[str]) -> str:
    return load_page(config.TEMPLATE_WEATHER_DUMMY, {'options': get_form_options(cities)})


def cities(cities_data: tuple[str, float, float]) -> str:
    cities_html = get_html_list(cities_data) if cities_data else 'No cities found'
    return load_page(config.TEMPLATE_CITIES, {'cities': cities_html})


def get_html_list(cities_data: tuple):
    html = '<ul>{0}</ul>'
    href = 'href="/weather?city='
    inner = []
    lt, ln = 'latitude', 'longtitude'
    for city, lat, lon in cities_data:
        fixed = spaces_to_plusses(city)
        inner.append(f'<li><a {href}{fixed}">{city}</a> {lt}: {lat}, {ln}: {lon}</li>')
    return html.format(''.join(inner))


def get_form_options(options: list[str]) -> str:
    return '\n'.join(f'<option value="{option}">{option}</option>' for option in options)
