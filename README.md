# Beaver 

Beaver is a code generation tool which can accept an input structure
(json, yaml, ini, or xml) along with a template file, and produces code
by combining the two.

It uses Jinja2 for templating.


## Installing 

```bash
pip install -e git+https://github.com/clagraff/beaver.git#egg=beaver
```

## tl;dr

```bash
$ beaver one template.tpl data.json                                     # generate code and print to STDOUT
$ beaver one template.tpl stuff.yaml -o my_code.cpp                     # generate code and write to file
$ beaver one template.tpl config.ini --post indent -st -o indented.c    # generate code, indent the code, write to file

$ beaver many template.tpl {{__name__}}.cpp *.json                      # generate code from JSON files, write to .cpp files
$ beaver many templates.tpl foo{{__index__}}.c *.yaml --post indent -st # generate code from yaml files, write to .cpp files after indenting.
```

## Generate Code
### Data Formats
Beaver supports the following input formats for data:

* JSON
* Yaml
* XML
* INI

... with plans to include some additional format types.

### Templating
Beaver uses [Jinja2](http://jinja.pocoo.org/docs) for templating. This means you
can leaverage Jinja [filters](http://jinja.pocoo.org/docs/2.9/templates/#list-of-builtin-filters)
and [functions](http://jinja.pocoo.org/docs/2.9/templates/#list-of-global-functions), 
along with all the other niceties that come with using Jinja.

Never used Jinja2 before? You can learn how to [get started](http://jinja.pocoo.org/docs/2.9/intro/) or jump specifically
to their [template documention](http://jinja.pocoo.org/docs/2.9/templates/)


### Generate one file
To generate one specific file, you can use the `one` sub-command. You must specify
a Jinja2 template of the code structure, and the input data (JSON, Yaml, XML, 
or INI) file.

The command will output to STDOUT by default, unless the `-o` flag is used to
specify an output file.

```bash
$ beaver one template.tpl input.json -o output.code
```

### Generate multiple files
To generate multiple files at once, you can use the `many` sub-command.

```bash
$ beaver one template.tpl one_output_file.java input_1.json input_2.xml input_3.yaml
$ beaver one template.tpl one_output_file.java *.{json,xml,yaml} 
```

### Real-world example

Let's pretend we want to a Golang struct based on a Yaml file. Here are the two
files:

*struct.tpl*
```go
// {{ name }} is a test struct
type {{ name }} struct {
{% for key in attributes -%}
    {%- set attr = attributes[key] -%}
    {{ key }}   {{ attr.type }}{% if attr.json %} `json:"{{ attr.json }}"`{% endif %}
{% endfor -%}
}

// Print will print out the contents of {{ name }}
func ({{ name[0] }} {{ name }}) Print() {
    fmt.Println("{{ name }}: ")
{% for key in attributes -%}
    fmt.Println("{{ key }} -", {{ name[0] }}.{{ key }})
{% endfor -%}
}
```

*data.yaml*
```yaml
name: MyAwesomeStruct
attributes:
    ID:
        type: "*int64"
        json: id
    Data:
        type: float64
        json: "-"
    Secret:
        type: string
    DBConn:
        type: sql.DB
        json: conn
```

To generate code, we can run:

```bash
$ beaver one struct.tpl data.yaml -o struct.go
$ cat struct.go
// MyAwesomeStruct is a test struct
type MyAwesomeStruct struct {
ID   *int64 `json:"id"`
Data   float64 `json:"-"`
Secret   string
DBConn   sql.DB `json:"conn"`
}

// Print will print out the contents of MyAwesomeStruct
func (M MyAwesomeStruct) Print() {
    fmt.Println("MyAwesomeStruct: ")
fmt.Println("ID -", M.ID)
fmt.Println("Data -", M.Data)
fmt.Println("Secret -", M.Secret)
fmt.Println("DBConn -", M.DBConn)
}
```

Hmm. Unfortunately that code is not quite formatted right. But no worries!

We can use some post-rendering commands to fix it. These commands will execute against
the code after it is rendered, but before it is outputted.

```bash
$ beaver one struct.tpl data.yaml --post gofmt --post goimports -o struct.go
$ cat struct.go
import (
	"database/sql"
	"fmt"
)

// MyAwesomeStruct is a test struct
type MyAwesomeStruct struct {
	ID     *int64  `json:"id"`
	Data   float64 `json:"-"`
	Secret string
	DBConn sql.DB `json:"conn"`
}

// Print will print out the contents of MyAwesomeStruct
func (M MyAwesomeStruct) Print() {
	fmt.Println("MyAwesomeStruct: ")
	fmt.Println("ID -", M.ID)
	fmt.Println("Data -", M.Data)
	fmt.Println("Secret -", M.Secret)
	fmt.Println("DBConn -", M.DBConn)
}
```

## Contributing

Please read [CONTRIBUTING.md](https://gist.github.com/clagraff/a6fc2de504aa0a37bb87c951ccb73ec0) for details on our code of conduct, and the process for submitting pull requests to us.

## Versioning

We use [SemVer](http://semver.org/) for versioning. For the versions available, see the [tags on this repository](https://github.com/clagraff/beaver/releases). 

## Authors

* **Curtis  La Graff** - *Author* - [Profile](https://github.com/clagraff)

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details
