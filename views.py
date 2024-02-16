import config


def main() -> str:
    with open(config.TEMPLATE_MAIN, 'r') as file:
        return file.read()
    

def weather(weather_data: dict) -> str:
    with open(config.TEMPLATE_WEATHER, 'r') as file:
        return file.read().format(**weather_data)


def cities(cities: str) -> str:
    with open(config.TEMPLATE_CITIES, 'r') as file:
        return file.read().format(cities=cities)
