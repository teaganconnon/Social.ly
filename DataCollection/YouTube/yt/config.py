import json

with open('YouTube/.env.json') as env:
    env_dict = json.load(env)
    LOG_LEVEL = env_dict['LOG_LEVEL']
    API_KEYS = env_dict['API_KEYS']
    DATADIR = env_dict['DATADIR']
