Core
====

If you want to contribute to the project, or you simply wants to use this library as base to build your own models, in this page you will find the basic concept you must know.

Installation
------------

PyPlants is included in PyPI and can be installed using the following command:

.. code-block:: console

	$ python -m pip install pyplants

Contribute
----------

If you want to contribute, first clone the library and then install it in edit mode.

.. code-block:: console

	$ python -m pip install -e .

This method is suggested only if you are actively working to the package source code. If you want to build the package you can do it in this way.

.. code-block:: console

	$ python -m build

Of course you need a properly set python build environment.

Models architecture
-------------------

In pyplants a model is designed as a simple python class that inherit by one of the available base classes. :class:`BaseDisease <pyplants.core.base.BaseDisease>` is used for disease models, :class:`BasePhenology <pyplants.core.base.BasePhenology>` for phenology models. Regardless the type, concrete models must strictly follow the following schema:

* provide a proper implementation for the :code:`_update_imp` method
* define a class attribute :code:`_model_meta` as a :code:`dict` with metadata regarding the model

In the following table, the possible :code:`_model_meta` fields are reported.

============== ========================================================= =================================
Field          Type                                                      Description
============== ========================================================= =================================
timestep       String                                                    Update timestep ('h' or 'd')
use_ctx_fields Set of :class:`CtxField <pyplants.core.context.CtxField>` Required fields in context
bbch_range     Tuple of integer                                          Valid BBCH range for model update
============== ========================================================= =================================

For phenology models, as soon as a new BBCH stage is reached, the internal :class:`BBCHScale <pyplants.phenology.scales.BBCHScale>` must be updated. Disease models, instead, must append a new :class:`DiseaseEvent <pyplants.diseases.common.DiseaseEvent>` to the events list each time the :code:`update` method is invoked.

If a disease model uses phenology data, :class:`BaseDiseaseWithPhenology <pyplants.core.base.BaseDiseaseWithPhenology>` has to be used as parent class, and a phenology model must be provided in the constructor. If a bbch_range is defined in the :code:`_model_meta`, the model will be automatically executed only when the current BBCH stage falls in the provided range.

Finally, models automatically check the :code:`UpdateCtx` validity: a :code:`ValueError` is raised if one of the mandatory fields (listed inside :code:`use_ctx_fields`) is missing, or an invalid timestep is provided.

Your first custom model
^^^^^^^^^^^^^^^^^^^^^^^

The rule of three ten is a simple model to detect *downy mildew* of the grape. It is a daily model that predicts primary infections when a simple empirical rule is met. Nowadays, it is considered a very outdated tool; however, it serves well to show how to write a custom model.

.. code-block:: python

	from pyplants.core.context import UpdateCtx
	from pyplants.core.context import CtxField
	from pyplants.core.base import BaseDiseaseWithPhenology
	from pyplants.diseases.common import DiseaseEvent


	class ThreeTen(BaseDiseaseWithPhenology):
	   """Simple three-ten rule for downy mildew of the grape."""
	   _model_meta = {
	      "timestep": "d",
	      "use_ctx_fields": {CtxField.TMEAN, CtxField.RAIN}
	      "bbch_range": (5, 75)
	   }

	   def _update_imp(self, update_ctx: UpdateCtx):
	      rain = update_ctx.rain
	      tmean = update_ctx.tmean
	      # The rule can be estimated using context data
	      inf = rain >= 10 and tmean >= 10
	      # Append the new event on the list
	      # (infection must be converted in float)
	      self._events.append(DiseaseEvent(
	         dt=update_ctx.dt,
	         infection=float(inf)))

If you want to use this model, you can simply create an instance of it and call the :code:`update` method. Moreover, since this basic model relies on knowing the plant's shoot length, a phenological model is needed to estimate the BBCH stage. Therefore, in this example, we instantiate the :class:`Iphen <pyplants.phenology.iphen.Iphen>` model and we pass it to the constructor.

.. code-block:: python

	from pyplants.phenology.iphen import Iphen
	from pyplants.utils.plants import PlantEnum

	iphen = Iphen.build_from_plant(PlantEnum.GRAPE, "CHARDONNAY")
	custom = ThreeTen(iphen)

	iphen.update(update_ctx)
	custom.update(update_ctx)

Base classes
------------

These are the base classes that compose the core of the library.

.. autoclass:: pyplants.core.base.Model
	:members:
	:private-members:
	:member-order: bysource

.. autoclass:: pyplants.core.base.BasePhenology
	:members:
	:member-order: bysource

.. autoclass:: pyplants.core.base.BaseDisease
	:members:
	:member-order: bysource
	:private-members:

.. autoclass:: pyplants.core.base.BaseDiseaseWithPhenology
	:members:
	:member-order: bysource
	:private-members:

.. autoclass:: pyplants.core.context.UpdateCtx
	:members:
	:member-order: bysource
	:private-members:

.. autoclass:: pyplants.core.context.CtxField
	:members:
	:member-order: bysource
