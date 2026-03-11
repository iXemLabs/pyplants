Diseases
========

This package is composed by different modules, one for each disease. The currently supported diseases are listed below:

- PM: Powdery Mildew

Each model is implemented as a python class that inherit from one of the possible base classes in :code:`pyplants.diseases.base`. To run the model users should invoke the :code:`update` method passing a valid :code:`pyplants.utils.UpdateCtx` object. It is worth to say that internal :code:`_update_imp` should never be invoked in the client code.

Each model automatically check the presence of the input variables inside the update context, if a required field is missing an exception is rised. Results are stored inside the :code:`events` property, a list that contains an entry for each time the method :code:`update` is invoked.

Powdery Mildew
--------------

The :code:`pyplants.diseases.pm` module currently includes four different models to predict ascospore release events and infection events. The following table is a summary of the implemented models and the main features.

================  ========  =================  =========
Model             Timestep  Ascospore Release  Infection
================  ========  =================  =========
Gadoury [1]_      Daily     Yes                Yes
Moyer [2]_        Daily     Yes                No
Davis [3]_        Hourly    Yes                No
Caffi [5]_        Daily     Yes                Yes
================  ========  =================  =========

Following the details regarding each model.

.. autoclass:: pyplants.diseases.pm.Gadoury
	:show-inheritance:
	:members:
	:member-order: bysource

.. autoclass:: pyplants.diseases.pm.Moyer
	:show-inheritance:
	:members:
	:member-order: bysource

.. autoclass:: pyplants.diseases.pm.DavisRI
	:show-inheritance:
	:members:
	:member-order: bysource

.. autoclass:: pyplants.diseases.pm.Caffi
	:show-inheritance:
	:members:
	:member-order: bysource


Base Classes
------------

Each model should hinerit from one of these base classes. When no phenology hints is required the :code:`BaseDisease` class should be used, on the countrary :code:`BaseDiseaseWithPhenology`. This is relevant only if you wish to develop your own model compatible with this package.

.. autoclass:: pyplants.diseases.base.BaseDisease
	:members:
	:member-order: bysource
	:private-members:

.. autoclass:: pyplants.diseases.base.BaseDiseaseWithPhenology
	:members:
	:member-order: bysource
	:private-members:

The :code:`pyplants.diseases.base.DiseaseEvent` class include the output computed to each update.

.. autoclass:: pyplants.diseases.base.DiseaseEvent
	:members:
	:member-order: bysource

.. rubric:: References

.. [1] Gadoury, D. M., & Pearson, R. C. (1990). Ascocarp dehiscence and ascospore discharge in Uncinula necator. Phytopathology, 80(4), 393-401
.. [2] Moyer, M. M., Gadoury, D. M., Wilcox, W. F., & Seem, R. C. (2014). Release of Erysiphe necator ascospores and impact of early season disease pressure on Vitis vinifera fruit infection. American Journal of Enology and Viticulture, 65(3), 315-324
.. [3] Gubler, W. D., Rademacher, M. R., Vasquez, S. J., & Thomas, C. S. (1999). Control of powdery mildew using the UC Davis powdery mildew risk index. APSnet Feature
.. [4] Mills, W. D. (1944). Efficient use of sulfur dust and sprays during rain to control apple scab. NY State Agr. Expt. Sta., Ithaca. Ext. Bul, 630.
.. [5] Caffi, T., Rossi, V., Legler, S. E., & Bugiani, R. (2011). A mechanistic model simulating ascosporic infections by Erysiphe necator, the powdery mildew fungus of grapevine. Plant Pathology, 60(3), 522-531