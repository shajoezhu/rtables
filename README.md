# ghm: The Selective Github Migration Utility

`ghm`, which stands for Github Migrator, is a CLI that allows one to migrate from one Github instance to another.

The following migrations are supported:

| From              | To                |
|-------------------|-------------------|
| Github Enterprise | Github Cloud      |
| Github Cloud      | Github Enterprise |
| Github Enterprise | Github Enterprise |


## Requirements

* Python 3.6+
## Installation

Install `ghm` by running:

```bash
python setup.py install
ghm --version
```

Alternatively, you may build and use the Docker image as follows:

```bash
docker build -t ghm:latest .
docker run -it --rm ghm:latest --version
```

## Usage

* Create a configuration file by referring to the [`schema.yaml`](ghm/conf/schema.yaml) file. An [example configuration file](example.yaml) can be found in the root directory of this repository.
* Run:
    ```bash
    ghm -c <configuration file>
    ```

## API Documentation

This project uses [`pdoc3`](https://github.com/pdoc3/pdoc) to generate docs via docstrings.
You may generate docs by running:

```bash
pdoc --html ghm
```
