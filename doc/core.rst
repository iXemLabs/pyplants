Core
====

If you want to contribute to the project, or you simply wants to use this library as base to build own models for your projects, in this page you will find the basic concept you must know.

Installation
------------

For the moment, pyplants is not yet included in PyPi, therefore you need a source distribution (a *tar.gz* file) or a wheel. You can install it locally by using the following command:

.. code-block:: console

	(.venv) $ python -m pip install pyplants-x.y.z.tar.gz

Please change *x.y.z* with the provided package version. Alternatively, you can install pyplants in edit mode by running this command inside the root of the project:

.. code-block:: console

	(.venv) $ python -m pip install -e .

This method is suggested only if you are actively working to the package source code. If you want to build the package you can do it in this way.

.. code-block:: console

	(.venv) $ python -m build --sdist

Of course you need a properly set python build environment.

Models architecture
-------------------

In pyplants two possible base models exists: :class:`BaseDisease <pyplants.core.base.BaseDisease>` for disease models and :class:`BasePhenology <pyplants.core.base.BasePhenology>` for phenology model. In general, a model is designed as simple python class that inherit by one of the available base classes. Regardless the type, concrete model must provide a proper implementation for the :code:`_update_imp` method.

For the phenology models, as soon as a new BBCH stage is reached, the internal :class:`BBCHScale <pyplants.phenology.scales.BBCHScale>` must be updated.

A disease model, instead, must implements two abstract methods:

* :code:`_update_imp`: to react on a new update context
* :code:`req_update_ctx_fields`: returning a set of required fields inside the context

PyPlants will automatically check the update context for the mandatory fields, a :code:`ValueError` is raised if one of the requested field inside the context is set to :code:`None`.

Additionally, when a disease model requires phenology data, it must inherit by :class:`BaseDiseaseWithPhenology <pyplants.core.base.BaseDiseaseWithPhenology>`. In this case, the parent constructor can be used to pass down a phenology model and an optional python tuple with the BBCH period. If provided, the model will be automatically executed only when the current BBCH stage falls in the provided range.

Your first custom model
^^^^^^^^^^^^^^^^^^^^^^^

The rule of the three ten is a simple model to detect *downy mildew*. It is a daily model that predicts primary infections when a simple empirical rule is met. Nowadays, it is considered a very outdated tool; however, it serves well to show how to write your custom model

.. code-block:: python

	from typing import Set

	from pyplants.core.context import UpdateCtx
	from pyplants.core.base import BaseDiseaseWithPhenology
	from pyplants.diseases.common import DiseaseEvent


	class ThreeTen(BaseDiseaseWithPhenology):
	   """Simple three-ten rule for downy mildew of the grape."""
	   START_BBCH = 5
	   END_BBCH = 75

	   def __init__(self, phen_model):
	      super().__init__(
	         phen_model,
	         (ThreeTen.START_BBCH, ThreeTen.END_BBCH))

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
	
	   @property
	   def req_update_ctx_fields(self) -> Set[str]:
	      return {"tmean", "rain"}

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
