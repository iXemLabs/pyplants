.. pyplants documentation master file, created by
   sphinx-quickstart on Fri Jun 20 12:26:45 2025.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

PyPlants
========

PyPlants is a collection of disease and phenological models for plants. The main purpose of this library is to enable both developers and researchers to use models described in the scientific literature.

PyPlants is designed with ease in mind, all the models implement a common software interface hiding the implementation details. Additionally, basic support to develop custom models is provided.

Getting Started
---------------

In this example we initialize a simple disease model for *powdery mildew* (pm), and we run it using the :code:`update` method.

.. code-block:: python

   from datetime import datetime

   from pyplants.core.context import UpdateCtx
   from pyplants.diseases.grape.pm import Moyer

   model = Moyer()
   # Update the model with input data...
   model.update(
      UpdateCtx(dt=datetime(2026, 1, 1, 0, 0), tmax=5, rain=0))
   # You call update when a new update context is available
   # The output of the model is stored inside the events property
   model.events

UpdateCtx is an utility that contains the agrometeorological data. Users should fill the update context with new data and then invoke the :code:`update` method. The time step depends on the specific model, in this example the selected model runs on a daily basis.

Finally, each model exposes an events list containing the output computed during each update.

.. topic:: Note

   For insight regarding each specific model, original papers are quoted in the documentation.

.. toctree::
   :hidden:
   :maxdepth: 2
   
   core
   diseases
   phenology
