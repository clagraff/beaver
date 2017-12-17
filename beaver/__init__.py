#!/usr/bin/env python
# coding: utf-8
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

__license__ = 'MIT License'

import argparse
import glob
import os
import subprocess

import jinja2

import beaver.cli as cli
import beaver.drivers as drivers



def run(cmd, stdin):
    """ Execute the specified command, providing input into the process as
    provided by the "stdin" string.
    """
    proc = subprocess.Popen(
        cmd.split(" "),
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        shell=True,
    )

    utf8_encoded = stdin.encode("utf-8")
    out = proc.communicate(utf8_encoded)[0]
    utf8_decoded = out.decode("utf-8")

    retcode = proc.returncode

    if retcode != 0:
        raise Exception(
            "External command: %s returned non-zero exit status: %s" % (
                cmd, retcode
            )
        )

    return utf8_decoded


def path_context(path):
    """Return a dictionary containing information about the specified path. """
    ctx = {}

    name = os.path.basename(path)

    ctx["__file__"] = name
    ctx["__name__"] = name.split(".")[0]
    ctx["__ext__"] = name.split(".")[-1]
    ctx["__dir__"] = os.path.dirname(path)
    ctx["__path__"] = path

    return ctx


def write_output(in_path, out_path, ctx):
    """Output to the `out_put` based on the result of rendering the input
    file with the templating context specified.
    """
    tpl = jinja2.Template(out_path)
    output_ctx = path_context(in_path)

    ctx_copy = dict(ctx)
    ctx_copy.update(output_ctx)

    return tpl.render(ctx_copy)


def load_template(path):
    """Load a jinja template from the specified file path. """
    contents = ""
    with open(path, 'r') as template_file:
        contents = template_file.read()

    tpl = jinja2.Template(contents)
    return tpl


def do_one(namespace):
    """Process the generation of just one output file. """
    if not os.path.isfile(namespace.template):
        raise Exception("Invalid template file path")
    if not os.path.isfile(namespace.input):
        raise Exception("Invalid input file path")

    context = drivers.parse(namespace.input)
    tpl = load_template(namespace.template)

    rendered = tpl.render(**context)

    if namespace.post:
        for cmd in namespace.post:
            rendered = run(cmd, rendered)

    if namespace.output:
        context["__index__"] = 0
        output_path = write_output(namespace.input, namespace.output, context)

        with open(output_path, 'w') as output_file:
            output_file.write(rendered)
    else:
        print(rendered)


def do_many(namespace):
    """Process the generation of multiple (more-than-one) output files ."""
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

    for idx, input_file in enumerate(inputs):
        context = drivers.parse(input_file)
        tpl = load_template(namespace.template)

        rendered = tpl.render(**context)

        if namespace.post:
            for cmd in namespace.post:
                rendered = run(cmd, rendered)

        context["__index__"] = idx
        output_path = write_output(input_file, namespace.output, context)

        with open(output_path, 'w') as output_file:
            output_file.write(rendered)

def main():
    """Create the parser and attempt to parse the program's arguments. """
    parser = cli.create_parser()

    namespace = parser.parse_args()
    command = namespace.command

    if not command:
        parser.print_help()
    elif command not in ['one', 'many']:
        raise Exception("Invalid command: %s" % command)

    if command == 'one':
        do_one(namespace)
    elif command == 'many':
        do_many(namespace)

if __name__ == "__main__":
    main()
