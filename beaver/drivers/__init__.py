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
            return fn(*args, **kwargs)
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
