from configparser import ConfigParser
import requests
import pprint


class ApiController:
    def __init__(self, api_domain, api_key):
        self.domain = api_domain
        self.key = api_key

    def request(self, method_url, **kwargs):
        # Генерируем кастомный GET-запрос с поддержкой массивов в аргументах
        url = f'{self.domain}{method_url}?API-Key={self.key}'
        for (key, value) in kwargs.items():
            if type(value) is list:
                for i in value:
                    url += f'&{key}[]={i}'
            elif type(value) is dict:
                for i, j in value.items():
                    url += f'&{key}[{i}]={j}'
            else:
                url += f'&{key}={value}'

        response = requests.get(url)
        return response.json()

    def get_offer_info(self, offer_id):
        return self.request(f'/3.0/offer/{offer_id}')['offer']

    def get_conversions_list(self, date_from='2020-07-01'):
        return self.request('/3.0/stats/conversions', date_from=date_from)['conversions']


if __name__ == '__main__':
    """
    Странная у вас документация API, входные параметры описаны, а что значат выходные - нет, 
    и некоторые выходные из рельных запросов в примерах документации вообще не встречаются, 
    пришлось некоторые вещи самому додумывать :)
    """
    # Инициализируем API
    config = ConfigParser()
    config.read('config.ini')
    api_ctrl = ApiController(config['DEFAULT']['api_domain'], config['DEFAULT']['api_key'])

    # Получаем информацию об оффере
    offer_info = api_ctrl.get_offer_info(660)
    print(f'Offer ID: {offer_info["id"]} \tTitle: \"{offer_info["title"]}\"')

    # Получаем список доступных стран
    # В некоторых офферах, которые я находил не было списка доступных стран,
    # были только списки таргетных стран, либо стран запрещенных для таргетирования
    # Поэтому либо берем список доступных стран, либо собираем его из таргетных групп
    country_list = api_ctrl.request('/3.1/countries')['countries']
    allow_countries = []
    if 'countries' not in offer_info:
        for target_group in offer_info['targeting']:
            if target_group['country']['allow']:
                allow_countries += [country_info for country_info in country_list
                                    if country_info['code'] in target_group['country']['allow']]
            elif target_group['country']['deny']:
                allow_countries += [country_info for country_info in country_list
                                    if country_info['code'] not in target_group['country']['deny']]
            else:
                allow_countries = country_list
    else:
        allow_countries += [country_info for country_info in country_list
                            if country_info['code'] in offer_info['countries']]

    print('Доступные страны для данного оффера:')
    print([country['name'] for country in allow_countries])

    print('.............................................')

    # Получаем все доступные конверсии,
    # но нам доступна только одна (скорее всего подстроено составителями задания)
    # Почему-то в доступной конверсии нет параметра 'clickid', хотя в документации он указан
    # зато есть 'cbid', мне кажется это одно и тоже, и расшифровывается как "click by id",
    # он совпадает с параметром 'action_id', который в примере документации совпадает с 'clickid'
    conversions_list = api_ctrl.get_conversions_list()
    for conversion_info in conversions_list:
        print(f'Найдена конверсия "{conversion_info["id"]}", относящаяся к офферу "{conversion_info["offer_id"]}"')
        if conversion_info['offer_id'] == offer_info['id']:
            print('Конверсия относится к данному офферу')
            print(f'ClickID: {conversion_info["cbid"]}')
            print(f'Конверсия из: {conversion_info["country_name"]}, {conversion_info["city"]}')
        else:
            print('Конверсия не относится к данному офферу')
