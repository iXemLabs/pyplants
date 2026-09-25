.. pyplants documentation master file, created by
   sphinx-quickstart on Fri Jun 20 12:26:45 2025.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

PyPlants
========

.. image:: https://github.com/iXemLabs/pyplants/actions/workflows/tests.yml/badge.svg
   :target: https://github.com/iXemLabs/pyplants/actions/workflows/tests.yml

.. image:: https://img.shields.io/badge/DOI-10.1016%2Fj.softx.2026.103062-blue
   :target: https://doi.org/10.1016/j.softx.2026.103062

.. image:: https://img.shields.io/badge/License-Apache_2.0-blue.svg
   :target: https://github.com/iXemLabs/pyplants/blob/main/LICENSE 

PyPlants is a collection of disease and phenological models for plants. The main purpose of this library is to enable both developers and researchers to use models described in the scientific literature.

PyPlants is designed with ease in mind, models implement a common software interface hiding the implementation details. Additionally, basic support to develop custom models is provided.

Getting Started
---------------

In this example, we use a simple ascospore prediction model for *powdery mildew* of the grape. To run a model, simply invoke the :code:`update` method passing the :code:`UpdateCtx` in input, a convenient data struct to hold agrometeorological data.

.. code-block:: python

   >>> from datetime import datetime
   >>> from pyplants.core.context import UpdateCtx
   >>> from pyplants.diseases.grape.pm import Moyer
   >>> # Moyer et al. ascospore release model
   >>> model = Moyer()
   >>> # Create dummy data
   >>> dt = datetime(2026, 1, 1, 0, 0)
   >>> uctx = UpdateCtx(dt=dt, tmax=5, rain=0, step="d")
   >>> model.update(uctx)
   >>> model.events[0]
   DiseaseEvent(
      dt=datetime.datetime(2026, 1, 1, 0, 0),
      spore_release=0.0,
      infection=None,
      extra_fields={'asc_p': 0.035371388525063274})

The time step depends on the specific model, in this example, the selected model runs on a daily basis. Finally, each model exposes an events list containing the output computed during each update.

.. topic:: Note

   For insight regarding each specific model, original papers are quoted in the documentation.

.. toctree::
   :hidden:
   :maxdepth: 2
   
   core
   diseases
   phenology
