Grape
=====

In this module the disease models related to the grape are grouped. Currently, the following disease are supported:

* Powdery Mildew (PM)
* Grey Mould (GM)
* Downy Mildew (DM)

Powdery Mildew
--------------

The :code:`pyplants.diseases.grape.pm` module currently includes four different models to predict ascospore release risk and infection risk. The following table is a summary of the implemented models and the main features.

================  ========  =============  =========
Model             Timestep  Spore Release  Infection
================  ========  =============  =========
Gadoury [1]_      Daily     Yes            Yes
Moyer [2]_        Daily     Yes            No
Davis [3]_ [4]_   Hourly    Yes            No
Caffi [5]_        Daily     Yes            Yes
================  ========  =============  =========

The :code:`spore_release` field in :code:`DiseaseEvent` is used to report the ascospore release risk. Following the details about each model.

.. autoclass:: pyplants.diseases.grape.pm.Gadoury
	:show-inheritance:
	:members:
	:member-order: bysource

.. autoclass:: pyplants.diseases.grape.pm.Moyer
	:show-inheritance:
	:members:
	:member-order: bysource

.. autoclass:: pyplants.diseases.grape.pm.DavisRI
	:show-inheritance:
	:members:
	:member-order: bysource

.. autoclass:: pyplants.diseases.grape.pm.Caffi
	:show-inheritance:
	:members:
	:member-order: bysource

Grey Mould
----------

The :code:`pyplants.diseases.grape.gm` module currently includes only three models to predict the infection risk. The following table is a summary of the implemented models and the main features.

================  ========  =============  =========
Model             Timestep  Spore Release  Infection
================  ========  =============  =========
Broome [6]_       Hourly    No             Yes
GoFe [7]_         Hourly    No             Yes
GoDom [8]_        Daily     No             Yes
================  ========  =============  =========

Following the details about each model.

.. autoclass:: pyplants.diseases.grape.gm.Broome
	:show-inheritance:
	:members:
	:member-order: bysource

.. autoclass:: pyplants.diseases.grape.gm.GoFe
	:show-inheritance:
	:members:
	:member-order: bysource

.. autoclass:: pyplants.diseases.grape.gm.GoDom
	:show-inheritance:
	:members:
	:member-order: bysource

Downy Mildew
------------

The :code:`pyplants.diseases.grape.dm` module currently includes only one model to predict infection risk. The following table is a summary of the implemented models and the main features.

================  ========  =============  =========
Model             Timestep  Spore Release  Infection
================  ========  =============  =========
Plasmo [9]_       Hourly    No             Yes
================  ========  =============  =========

Following the details about each model.

.. autoclass:: pyplants.diseases.grape.dm.Plasmo
	:show-inheritance:
	:members:
	:member-order: bysource

.. rubric:: References

.. [1] Gadoury, D. M., & Pearson, R. C. (1990). Ascocarp dehiscence and ascospore discharge in Uncinula necator. Phytopathology, 80(4), 393-401
.. [2] Moyer, M. M., Gadoury, D. M., Wilcox, W. F., & Seem, R. C. (2014). Release of Erysiphe necator ascospores and impact of early season disease pressure on Vitis vinifera fruit infection. American Journal of Enology and Viticulture, 65(3), 315-324
.. [3] Gubler, W. D., Rademacher, M. R., Vasquez, S. J., & Thomas, C. S. (1999). Control of powdery mildew using the UC Davis powdery mildew risk index. APSnet Feature
.. [4] Mills, W. D. (1944). Efficient use of sulfur dust and sprays during rain to control apple scab. NY State Agr. Expt. Sta., Ithaca. Ext. Bul, 630.
.. [5] Caffi, T., Rossi, V., Legler, S. E., & Bugiani, R. (2011). A mechanistic model simulating ascosporic infections by Erysiphe necator, the powdery mildew fungus of grapevine. Plant Pathology, 60(3), 522-531
.. [6] Broome, J. C., English, J. T., Marois, J. J., Latorre, B. A., & Aviles, J. C. (1995). Development of an infection model for Botrytis bunch rot of grapes based on wetness duration and temperature. Phytopathology, 85(1), 97-102
.. [7] González-Fernández, E., Piña-Rey, A., Fernández-González, M., Aira, M. J., & Rodríguez-Rajo, F. J. (2020). Identification and evaluation of the main risk periods of Botrytis cinerea infection on grapevine based on phenology, weather conditions and airborne conidia. The Journal of Agricultural Science, 158(1-2), 88-98.
.. [8] González-Domínguez, E., Caffi, T., Ciliberti, N., & Rossi, V. (2015). A mechanistic model of Botrytis cinerea on grapevines that includes weather, vine growth stage, and the main infection pathways. PloS one, 10(10), e0140444.
.. [9] Orlandini, S., Gozzini, B., Rosa, M., Egger, E., Storchi, P., Maracchi, G., & Miglietta, F. (1993). Plasmo: a simulation model for control of plasmopara viticola on grapevine 1. EPPO Bulletin, 23(4), 619-626.
