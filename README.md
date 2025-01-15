# foo2bar
foo2bar is a Python library designed to substitute values in variable assignments within a script. It enables you to analyze and modify Python code by replacing variable assignments with new values, providing a cleaner and more efficient approach compared to using regular expressions.

It provides a cleaner approach to value substitution compared to using regular expressions.

## Features

- Parse and analyze Python scripts.
- Substitute variable assignments with new values.
- Support for different scopes (global, class, method).
- Safe evaluation of expressions.

## Installation

To install foo2bar, use pip:

```sh
pip install foo2bar
```

## Quickstart

To quickly get started with foo2bar, let's consider an example. Suppose you have a script named `my_script.py`:

```python
from foo import do_stuff
my_duration = 10  # duration in seconds
print(do_stuff(my_duration))
```

You want to create a copy of this script, `my_new_script.py`, where `my_duration` is set to `0.5`. You can achieve this by running the following command in your terminal:

```sh
foo2bar my_script.py raw --output my_new_script.py --my_duration 0.5
```

After running the command, the newly created `my_new_script.py` will look like this:

```python
from foo import do_stuff
my_duration = 0.5  # duration in seconds
print(do_stuff(my_duration))
```


## Usage

### Command Line Interface

foo2bar provides a command line interface for substituting values in a script.

#### Substitute Raw

Raw substitution allows you to replace variable assignments with the provided values. Lists must be passed with brackets, dictionaries with curly braces, and strings with additional quotes. 

```sh
foo2bar <script_path> raw --output <output_path> --my_int 12323 --my_str ''foo bar'' --my_list '[baz, bat]' --my_dict '{a: 2.35, b: None}' --my_none "None"
```

This feature supports also more complex injections, like `'abs(5 - 10)'`.

> **Warning:** In order to inject a string, quotes must be escaped or doubled properly.

#### Substitute Typed [experimental]

Typed is syntactic sugar to interpret inputs with their types. 

```sh
foo2bar <script_path> typed --output <output_path> --x 12323 --s "foo bar" --my_typed_list "baz" "bat"
```

### Python API

You can also use foo2bar as a Python library:

```py
from foo2bar.wrapper import CodeWrapper

# Load a script
wrapper = CodeWrapper.from_file("path/to/your_script.py")

# Substitute values
wrapper.substitute_assign_values_global({"x": "100", "y": "200"})

# Get the modified code
print(wrapper.code)
```

## Development

### Running Tests

To run the tests, use the following command:

```sh
python -m unittest discover tests
```

### Contributing

Contributions are welcome! Please open an issue or submit a pull request on GitHub.

## License

This project is licensed under the MIT License.

## Contact

For any questions or inquiries, please contact Martin Favin-Lévêque at [mrtichou.dev@gmail.com](mailto:mrtichou.dev@gmail.com).
