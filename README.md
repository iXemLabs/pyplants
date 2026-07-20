# PyPlants

[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Tests](https://github.com/iXemLabs/pyplants/actions/workflows/tests.yml/badge.svg)](https://github.com/iXemLabs/pyplants/actions/workflows/tests.yml)

PyPlants is a collection of disease and phenological models for plants. The main purpose of this library is to enable both developers and researchers to use models described in the scientific literature.

### Usage

The package is subdivided in two main subpackages, `pyplants.phenology` and `pyplants.diseases`. In general, each model implements its own logic that can be invoked with the `update` method, which accept as input an `UpdateCtx` object containing your agrometeorological measures. 

Enjoy.
