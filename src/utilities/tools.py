import json
from jsonschema import validate
import os
from datetime import date
import re

FILE_PATH = os.path.dirname(__file__)

def validate_input(payl):
    with open(
        os.path.join(
            FILE_PATH,
            'input_schema.json'
        ), 'r'
    ) as j:
        input_schema = json.load(j)

    validate(instance=payl, schema=input_schema)

def select_subdict(dictionary, keys_to_select):
    for k in keys_to_select:
        if k not in dictionary.keys():
            raise ValueError('Trying to select a subdict with keys not contained on large dict.')
    
    dict_filter = lambda x, y: dict([ (i,x[i]) for i in x if i in set(y) ])
    small_dict=dict_filter(dictionary, keys_to_select)
    return small_dict

def camel(snake_str):
    first, *others = snake_str.split('_')
    return ''.join([first.lower(), *map(str.title, others)])

def camelize_dict(snake_dict):
    new_dict = {}
    if isinstance(snake_dict, dict):
        for key, value in snake_dict.items():
            new_key = camel(key)
            if isinstance(value, list):
                new_dict[new_key] = list(map(camelize_dict, value))
            if isinstance(value, dict):
                new_dict[new_key] = camelize_dict(value)
            else:
                new_dict[new_key] = value
        return new_dict
    else:
        return snake_dict