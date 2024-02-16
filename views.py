import config


def main() -> str:
    with open(config.TEMPLATE_MAIN, 'r') as template:
        return template.read()


def weather(weather_data: dict) -> str:
    with open(config.TEMPLATE_WEATHER, 'r') as template:
        return template.read().format(**weather_data)


def cities(cities_text: str) -> str:
    with open(config.TEMPLATE_CITIES, 'r') as template:
        return template.read().format(cities=cities_text)
