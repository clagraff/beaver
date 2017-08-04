import argparse
import glob
import os
import subprocess

import jinja2

import cli
import drivers



def run(cmd, stdin):
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
        raise Exception("External command: %s returned non-zero exit status: %s" % (cmd, retcode))

    return utf8_decoded


def path_context(path):
    ctx = {}

    name = os.path.basename(path)

    ctx["__file__"] = name
    ctx["__name__"] = name.split(".")[0]
    ctx["__ext__"] = name.split(".")[-1]
    ctx["__dir__"] = os.path.dirname(path)
    ctx["__path__"] = path

    return ctx


def write_output(in_path, out_path, ctx):
    tpl = jinja2.Template(out_path)
    output_ctx = path_context(in_path)

    ctx_copy = dict(ctx)
    ctx_copy.update(output_ctx)

    return tpl.render(ctx_copy)


def load_template(path):
    contents = ""
    with open(path, 'r') as f:
        contents = f.read()

    tpl = jinja2.Template(contents)
    return tpl


def do_one(namespace):
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

        with open(output_path, 'w') as f:
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

    for idx, input_file in enumerate(inputs):
        context = drivers.parse(input_file)
        tpl = load_template(namespace.template)

        rendered = tpl.render(**context)

        if namespace.post:
            for cmd in namespace.post:
                rendered = run(cmd, rendered)

        context["__index__"] = idx
        output_path = write_output(input_file, namespace.output, context)

        with open(output_path, 'w') as f:
            f.write(rendered)

def main():
    parser = cli.create_parser()

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
