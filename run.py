from configparser import ConfigParser
import requests


class ApiController:
    def __init__(self, api_domain, api_key):
        self.domain = api_domain
        self.key = api_key


if __name__ == '__main__':
    config = ConfigParser()
    config.read('config.ini')
    api_ctrl = ApiController(config['DEFAULT']['api_domain'], config['DEFAULT']['api_key'])
