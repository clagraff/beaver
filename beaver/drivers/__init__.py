import json
import configparser
import yaml
import xmldict


extension_handlers = {}


def get_ext(path):
    partitions = path.split(".")
    if len(partitions) <= 1:
        raise Exception("No extension on file path: %s" % path)
    return partitions[-1]

def parse(path):
    ext = get_ext(path)
    if ext not in extension_handlers:
        raise Exception("Extension not supported: %s" % ext)

    parser = extension_handlers[ext]
    return parser(path)


def register(ext):
    def outer(fn):
        extension_handlers[ext] = fn

        def inner(*args, **kwargs):
            fn(*args, **wkargs)
        return inner
    return outer


@register("json")
def parse_json(path):
    content = ""
    data = {}

    with open(path, "r") as f:
        content = f.read()

    if content:
        data = json.loads(content)

    return data


@register("yaml")
@register("yml")
def parse_yaml(path):
    data = {}

    with open(path, "r") as f:
        data = yaml.safe_load(f)

    return data


@register("ini")
def read_ini(path):
    data = {}

    parser = configparser.ConfigParser()
    parser.read(path)

    for section in parser:
        data[section] = {}
        for attr in parser[section]:
            data[section][attr] = parser[section][attr]

    return data

@register("xml")
def read_xml(path):
    content = ""
    data = {}

    with open(path, "r") as f:
        content = f.read()

    if content:
        data = xmldict.xml_to_dict(content)

    return data
