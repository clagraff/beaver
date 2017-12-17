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

import argparse



_ONE_EPILOG = """    Generate code for one file.

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


_MANY_EPILOG = """    Generate code for multiple files.

    flags and arguments:
        OUTPUT
            Specify the output for each of the generated files by passing a pattern
            which can be used to generate the file names. You can use jinja-style
            placeholders to either use information from the respective input file,
            or from constants which are specified below:

                {{__file__}}
                    The base filename of the input file.
                    Example: my_input.yaml

                {{__name__}}
                    The base name of the input file, without the extension.
                    Example: my_input

                {{__ext__}}
                    The extension of the input file.
                    Example: yaml

                {{__index__}}
                    An index representing how many previous input files have been
                    evauluated.
                    Example: 0

            If you specify an output which will not change, it will be overridden
            by whatever code was last generated during the process.

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

        INPUTS
            Specify one or more paths to an input files. You can also use glob
            patterns, (e.g.: *.json).

            These files can be a JSON, Yaml, INI, or XML file.
            The data represented in this file will be used to replace the placeholders
            present in the template.


"""


def populate_one_cmd(parser):
    """Populate the provided parent parser with a subcomand for generating only
    a single output file.
    """
    parser.add_argument('template', action='store', help='Path to the template file.',)
    parser.add_argument('input', action='store', help='Path to input file.',)
    parser.add_argument(
        '-o', action='store', dest="output",
        help='Path to output file instead of StdOut.',
    )
    parser.add_argument(
        '--post', action='append', dest="post", default=[],
        help='Command(s) which will receive the generated code after '
        'it is rendered.',
    )


def populate_many_cmd(parser):
    """Populate the provided parent parser with a subcommand for generating
    multiple output files.
    """
    parser.add_argument(
        'template', action='store', help='Path to the template file.'
    )
    parser.add_argument(
        'output', action='store',
        help='Output pattern for creating output files.'
    )
    parser.add_argument(
        'inputs', action='store', nargs="+", help='Input patterns'
    )
    parser.add_argument(
        '--post', action='append', dest="post", default=[],
        help='Command(s) which will receive the generated code after it '
        'is rendered.',
    )


def create_parser():
    """Creates and returns the main program parser. """
    parser = argparse.ArgumentParser(description='Beaver is a code generation tool.')
    subparsers = parser.add_subparsers(help='commands', dest='command')

    one = subparsers.add_parser(
        'one',
        help="Generate code for one file.",
        epilog=_ONE_EPILOG,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )


    many = subparsers.add_parser(
        'many',
        help='Generate code for multiple files.',
        epilog=_MANY_EPILOG,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    populate_one_cmd(one)
    populate_many_cmd(many)

    return parser
