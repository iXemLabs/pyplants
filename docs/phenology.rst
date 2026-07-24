Phenology
=========

Phenological models are used to predict growth stage of the crop. There are many models in the literature, but for  the moment, only one is implemented.

In general, every phenology model in pyplants will use the BBCH scale as a common way to keep track of phenology growth stages [1]_. BBCH is composed by two main phases: vegetative and reproductive. These two phases may occasionally overlap, for this reason they are separately stored.

BBCH Scale
----------

In general, users should not use directly the *BBCH* utilities. Phenological models must handle them automatically, however, if you want to develop your own model, this simple implementation can be useful.

The :code:`BBCHStage` class implements the overload for comparison operators. You can compare between :code:`BBCHStage` or integer values. Comparison is allowed only between stages falling in the same main phase (vegetative or reproductive).

.. autoclass:: pyplants.phenology.scales.BBCHStage
	:members:
	:member-order: bysource

.. autoclass:: pyplants.phenology.scales.BBCHRecord
	:members:
	:member-order: bysource

.. autoclass:: pyplants.phenology.scales.BBCHScale
	:members:
	:member-order: bysource

.. autoclass:: pyplants.phenology.scales.BBCHStageAlreadyReached

Iphen
-----

Model for plants phenology based on [2]_. This model uses only hourly mean temperature and internally compute the *Normal Hour Heat (NHH)*, using three cardinal temperatures [3]_. 

This implementation currently supports only grape plant.

.. autoclass:: pyplants.phenology.iphen.Iphen
	:show-inheritance:
	:members:
	:member-order: bysource
	:class-doc-from: both

.. rubric:: References

.. [1] Meier, U., Bleiholder, H., Buhr, L., Feller, C., Hack, H., Heß, M., ... & Zwerger, P. (2009). The BBCH system to coding the phenological growth stages of plants–history and publications. Journal für Kulturpflanzen, 61(2), 41-52.

.. [2] Mariani, L., Alilla, R., Cola, G., Monte, G. D., Epifani, C., Puppi, G., & Osvaldo, F. (2013). IPHEN—a real-time network for phenological monitoring and modelling in Italy. International journal of biometeorology, 57(6), 881-893.

.. [3] Wang, E., & Engel, T. (1998). Simulation of phenological development of wheat crops. Agricultural systems, 58(1), 1-24.