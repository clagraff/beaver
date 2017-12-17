"""MIT License

Copyright (c) 2017 Curtis La Graff

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import json
import configparser
import yaml
import xmldict


EXTENSION_HANDLERS = {}


def get_ext(path):
    """Retrieve the extension of the provided path. """
    partitions = path.split(".")
    if len(partitions) <= 1:
        raise Exception("No extension on file path: %s" % path)
    return partitions[-1]

def parse(path):
    """Parse the given path to return a dictionary containing the code
    generation context.
    """
    ext = get_ext(path)
    if ext not in EXTENSION_HANDLERS:
        raise Exception("Extension not supported: %s" % ext)

    parser = EXTENSION_HANDLERS[ext]
    return parser(path)


def register(ext):
    """Register a function as a given extension's parser. This is a decorator
    function.
    """
    def outer(wrapped_function):
        """Inner function for the outer decorator, which handles registering
        the provided function as an extension handler.
        """
        EXTENSION_HANDLERS[ext] = wrapped_function

        def inner(*args, **kwargs):
            """Used to return a way of executing the original function when
            desired.
            """
            return wrapped_function(*args, **kwargs)
        return inner
    return outer


@register("json")
def parse_json(path):
    """Parse a specified JSON file into a dictionary or list-object. """
    content = ""
    data = {}

    with open(path, "r") as input_file:
        content = input_file.read()

    if content:
        data = json.loads(content)

    return data


@register("yaml")
@register("yml")
def parse_yaml(path):
    """Parse a specified Yaml file into a dictionary. """
    data = {}

    with open(path, "r") as input_file:
        data = yaml.safe_load(input_file)

    return data


@register("ini")
def read_ini(path):
    """Parse a specified INI file into a dictionary. """
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
    """Parse a specified XML file into a dictionary or list-object. """
    content = ""
    data = {}

    with open(path, "r") as input_file:
        content = input_file.read()

    if content:
        data = xmldict.xml_to_dict(content)

    return data
