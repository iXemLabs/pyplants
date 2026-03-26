Contribute
==========

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

In pyplants two possible base models exists: :class:`BaseDisease <pyplants.diseases.base.BaseDisease>` for disease models and :class:`BasePhenology <pyplants.phenology.base.BasePhenology>` for phenology model. In general, a model is designed as simple python class that inherit by one of the available base classes.

A phenology model must implements the abstract update method. As soon as a new BBCH stage is reached, the internal :class:`BBCHScale <pyplants.phenology.scales.BBCHScale>` must be updated.

A disease model, instead, must implements two abstract methods:

* :code:`_update_imp`: to react on a new update context
* :code:`update_ctx_fields`: returning a set of required fields inside the context

PyPlants will automatically check the update context for the mandatory fields, a :code:`ValueError` is raised if one of the requested field inside the context is set to :code:`None`.

Additionally, when a disease model requires phenology data, it must inherit by :class:`BaseDiseaseWithPhenology <pyplants.disease.base.BaseDiseaseWithPhenology>`. In this case, the parent constructor can be used to pass down a phenology model and an optional python tuple with the BBCH period. If provided, the model will be automatically executed only between the BBCH period.

Example of custom model
^^^^^^^^^^^^^^^^^^^^^^^

The rule of the three ten is a simple model to detect *downy mildew*. It is a daily model that predict a primary infection when a simple empirical rule is met. Nowadays can be considered a very outdated tool, but it serves well for the purpose of show how to write your custom model. 

.. code-block:: python

	from pyplants.utils import UpdateCtx
	from pyplants.utils import DiseaseEvent
	from pyplants.diseases.base import BaseDiseaseWithPhenology


	class ThreeTen(BaseDiseaseWithPhenology):
	   """Simple three-ten base rule for downy mildew of the grape."""
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
	      # Append the event on the envets list
	      # (infection must be converted in float)
	      self._events.append(DiseaseEvent(
	         dt=update_ctx.dt,
	         infection=float(inf)))
	
	   @property
	   def update_ctx_fields(self):
	      return {"tmean", "rain"}

If you want to use this model, you can simply create an instance of it and call the :code:`update` method.

.. code-block:: python

	from pyplants.phenology.iphen import Iphen
	from pyplants.utils.plants import PlantEnum

	iphen = Iphen.build_from_plant(PlantEnum.GRAPE, "CHARDONNAY")
	custom = ThreeTen(iphen)

	custom.update(update_ctx)
