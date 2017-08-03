import argparse
import configparser
import glob
import json
import os
import subprocess

import jinja2
import yaml
import xmldict


def read_json(path):
    content = ""
    data = {}

    with open(path, "r") as f:
        content = f.read()

    if content:
        data = json.loads(content)

    return data


def read_yaml(path):
    data = {}

    with open(path, "r") as f:
        data = yaml.safe_load(f)

    return data

def read_ini(path):
    data = {}

    parser = configparser.ConfigParser()
    parser.read(path)

    for section in parser:
        data[section] = {}
        for attr in parser[section]:
            data[section][attr] = parser[section][attr]

    return data

def read_xml(path):
    content = ""
    data = {}

    with open(path, "r") as f:
        content = f.read()

    if content:
        data = xmldict.xml_to_dict(content)

    return data


EXTENSION_HANDLERS = {
    "ini": read_ini,
    "json": read_json,
    "xml": read_xml,
    "yaml": read_yaml,
    "yml": read_yaml,
}


def get_ext(path):
    partitions = path.split(".")
    if len(partitions) <= 1:
        raise Exception("No extension on file path: %s" % path)
    return partitions[-1]


def do_one(namespace):
    if not os.path.isfile(namespace.template):
        raise Exception("Invalid template file path")
    if not os.path.isfile(namespace.input):
        raise Exception("Invalid input file path")

    ext = get_ext(namespace.input)
    if ext not in EXTENSION_HANDLERS:
        raise Exception("Extension not supported: %s" % ext)

    context = EXTENSION_HANDLERS[ext](namespace.input)

    template_contents = ""
    with open(namespace.template, 'r') as f:
        template_contents = f.read()

    tpl = jinja2.Template(template_contents)
    rendered = tpl.render(**context)

    if namespace.post:
        for cmd in namespace.post:
            proc = subprocess.Popen(
                cmd.split(" "),
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                shell=True,
            )
            out = proc.communicate(rendered.encode("utf-8"))[0]
            rendered = out.decode("utf-8")

    if namespace.output:
        with open(namespace.output, 'w') as f:
            f.write(rendered)
    else:
        print(rendered)


def do_many(namespace):
    if not os.path.isfile(namespace.template):
        raise Exception("Invalid template file path")
    if not namespace.inputs:
        raise Exception("Must specify at least one input pattern")
    if not namespace.output:
        raise Exception("Must specify at least one output pattern")

    inputs = []
    for input_str in namespace.inputs:
        for filename in glob.iglob(input_str, recursive=True):
            inputs.append(filename)

    output_tpl = jinja2.Template(namespace.output)

    for idx, input_file in enumerate(inputs):
        ext = get_ext(input_file)
        if ext not in EXTENSION_HANDLERS:
            raise Exception("Extension not supported: %s" % ext)

        context = EXTENSION_HANDLERS[ext](input_file)

        template_contents = ""
        with open(namespace.template, 'r') as f:
            template_contents = f.read()

        tpl = jinja2.Template(template_contents)
        rendered = tpl.render(**context)

        if namespace.post:
            for cmd in namespace.post:
                proc = subprocess.Popen(
                    cmd.split(" "),
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    shell=True,
                )
                out = proc.communicate(rendered.encode("utf-8"))[0]
                rendered = out.decode("utf-8")

        output_context = dict(context)

        name = os.path.basename(input_file)
        output_context["__file__"] = name
        output_context["__name__"] = name.split(".")[0]
        output_context["__ext__"] = name.split(".")[-1]
        output_context["__dir__"] = os.path.dirname(input_file)
        output_context["__path__"] = input_file
        output_context["__index__"] = idx

        output = output_tpl.render(output_context)

        with open(output, 'w') as f:
            f.write(rendered)

def main():
    parser = argparse.ArgumentParser(description='Beaver is a code generation tool.')
    subparsers = parser.add_subparsers(help='commands', dest='command')


    one_epilog = """    Generate code for one file.

flags and arguments:
    -o OUTPUT
        If you specify an output file, generated code will be written to the file,
        creating it if necessary. It will override any content already in the file.

        If no output is specified, the generated code is displayed to STDOUT.

    --post POST
        You can specify multiple commands to run after the code has been generated, but
        before it is outputted/displayed.

        Each command will receive the generated code via STDIN. Changes made to the
        generated code will propogate to later commands.

        Commands are ran in the order they are received.

    TEMPLATE
        Specify a template which will be used to generate code files. The template file
        can contain Jinja2-style variables (e.g.: "{{foobar}}").\n

        These placeholders will be replaced by their counterparts as specified in the input file.

    INPUT
        Specify a path to an input file. This can be a JSON, Yaml, INI, or XML file.
        The data represented in this file will be used to replace the placeholders
        present in the template.


example:

    $ echo "package main\\ntype {{type_name}} struct{Conn *sql.DB}" > template.jinja
    $ echo '{"type_name": "MyCustomType"}' > input.json
    $ beaver one -o my_custom_type.go --post gofmt --post goimports template.jinja input.json"
    $ cat my_custom_type.go

        package main

        import "sql"

        type MyCustomType struct {
            Conn *sql.DB
        }

"""

    one = subparsers.add_parser(
        'one',
        help="Generate code for one file.",
        epilog=one_epilog,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    many = subparsers.add_parser('many', help='Generate code for multiple files.')

    one.add_argument('template', action='store', help='Path to the template file.',)
    one.add_argument('input', action='store', help='Path to input file.',)
    one.add_argument('-o', action='store', dest="output", help='Path to output file instead of StdOut.',)
    one.add_argument('--post', action='append', dest="post", default=[], help='Command(s) which will receive the generated code after it is rendered.',)

    many.add_argument('template', action='store', help='Path to the template file.')
    many.add_argument('output', action='store', help='Output pattern for creating output files.')
    many.add_argument('inputs', action='store', nargs="+", help='Input patterns')
    many.add_argument('--post', action='append', dest="post", default=[], help='Command(s) which will receive the generated code after it is rendered.',)

    namespace = parser.parse_args()
    command = namespace.command

    if command not in ['one', 'many']:
        raise Exception("Invalid command: %s" % command)

    if command == 'one':
        do_one(namespace)
    elif command == 'many':
        do_many(namespace)


if __name__ == "__main__":
    main()
