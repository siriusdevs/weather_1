import config
from typing import Optional

def load_page(template_path: str, formating: Optional[dict] = None):
    with open(template_path, 'r') as template:
        content = template.read()
    if formating:
        content = content.format(**formating)
    return content


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


def cities(cities: tuple[str, float, float]) -> str:
    cities_html = get_html_list(cities)
    return load_page(config.TEMPLATE_CITIES, {'cities': cities_html})


def get_html_list(cities):
    html = '<ul>{0}</ul>'
    href = 'href="/weather?city='
    inner = []
    for city, lat, lon in cities:
        inner.append(f'<li><a {href}{spaces_to_plusses(city)}">{city}</a> latitude: {lat}, longtitude: {lon}</li>')
    return html.format(''.join(inner))


def get_form_options(values: list[str]) -> str:
    print(values)
    return '\n'.join(f'<option value="{value}">{value}</option>' for value in values)
