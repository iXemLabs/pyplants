# PyPlants

This package is a collection of phenological and disease models as reported in different scientific papers.

### Install

Using this package is possible by installing it with the pip tool, at the moment the source distribution is the prefered way to build this package. The following command can be used to build pyplants.

```sh
python -m build --sdist
```

This will create a folder on your local machine named dist with a tar.gz archive. The package can then be installed with the following command:

```sh
python -m pip install pyplants-x.y.z.tar.gz
```

Please change the x.y.z with the proper version number.

### Usage

The package is subdivided in two main subpackages, `pyplants.phenology` and `pyplants.diseases`. For the moment you can refer to the docstring of the different models. In general, each model implements its own logic that can be invoked with the `update` method of each model. The idea is to keep the API as consistent as possible across the different models.

### Develop

If you want to improve this package it is highly suggested to install in develop mode, in this way change on the source code will be automatically reflected. You can do this with the following command.

```sh
python -m pip install -e .
```

Enjoy.
