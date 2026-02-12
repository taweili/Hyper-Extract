"""环境领域模板，用于生态和环保分析。"""

from .species_interaction import SpeciesInteractionNetwork
from .pollutant_impact import PollutantImpactMap
from .endangered_species import EndangeredSpeciesList

__all__ = [
    "SpeciesInteractionNetwork",
    "PollutantImpactMap",
    "EndangeredSpeciesList",
]
