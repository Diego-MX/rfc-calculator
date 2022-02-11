import json
from datetime import datetime as dt
from jsonschema import validate, exceptions
from flask import jsonify
from pathlib import Path

SITE = Path(__file__).parents[2]


def response_validate(payload, input_file):
    try: 
        with open(input_file, 'r') as _f:
            input_schema = json.load(_f)
        validate(instance=payload, schema=input_schema)
        an_object = {"error" : False}
    except exceptions.ValidationError as err:
        response = {
            "timestamp"     : str(dt.now()),
            "detail"        : str(err),
            "code"          : "0001",
            "type"          : "validation/input",
            "status_code"   : "400",
            "instance"      : "input/messages_strategy/invalid_structure" }
        an_object = {"error" : 400, "output" : (jsonify(response), 400)}
    return an_object


def select_subdict(a_dict, sub_keys):
    if not sub_keys.is_subset(a_dict.keys()):
        raise ValueError('Trying to select a subdict with keys not contained on large dict.')
    small_dict = dict((k, a_dict[k]) for k in sub_keys)
    return small_dict


def camel(snake_str):
    first, *others = snake_str.split('_')
    return ''.join([first.lower(), *map(str.title, others)])


def camelize_dict(snake_dict):
    if not isinstance(snake_dict, dict):
        return snake_dict

    def pass_value(a_val): 
        if isinstance(a_val, list):
            passed = list(map(camelize_dict, a_val))
        elif isinstance(a_val, dict):
            passed = camelize_dict(a_val)
        else:
            passed = a_val 
        return passed

    new_dict = dict((k, pass_value(v)) for (k, v) in snake_dict.items())
    return new_dict