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
Beaver supports two modes of code generation:
1. Single-file generation, using the `one` sub-command.
2. Multiple-file generatio, using the `many` sub-command.

### Generate one file
To generate one specific file, you can use the `one` command. You must specify
a Jinja2 template of the code structure, and the input data (JSON, Yaml, XML, 
or INI) file.

The command will output to STDOUT by default, unless the `-o` flag is used to
specify an output file.

```bash
$ beaver one template.tpl input.json -o output.code
```

#### Real-world example

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

## Running the tests

Explain how to run the automated tests for this system

### Break down into end to end tests

Explain what these tests test and why

```
Give an example
```

### And coding style tests

Explain what these tests test and why

```
Give an example
```

## Deployment

Add additional notes about how to deploy this on a live system

## Built With

* [Dropwizard](http://www.dropwizard.io/1.0.2/docs/) - The web framework used
* [Maven](https://maven.apache.org/) - Dependency Management
* [ROME](https://rometools.github.io/rome/) - Used to generate RSS Feeds

## Contributing

Please read [CONTRIBUTING.md](https://gist.github.com/PurpleBooth/b24679402957c63ec426) for details on our code of conduct, and the process for submitting pull requests to us.

## Versioning

We use [SemVer](http://semver.org/) for versioning. For the versions available, see the [tags on this repository](https://github.com/your/project/tags). 

## Authors

* **Billie Thompson** - *Initial work* - [PurpleBooth](https://github.com/PurpleBooth)

See also the list of [contributors](https://github.com/your/project/contributors) who participated in this project.

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details

## Acknowledgments

* Hat tip to anyone who's code was used
* Inspiration
* etc

