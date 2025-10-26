# amnezia-api/config.py
import os
import configparser

def get_config(path='files/setting.ini'):
    if not os.path.exists(path):
        raise FileNotFoundError("Файл files/setting.ini не найден. Выполните инициализацию.")
    config = configparser.ConfigParser()
    config.read(path)
    return {key: config['setting'][key] for key in config['setting']}