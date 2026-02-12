"""Environment domain templates for ecological and environmental analysis."""

from .species_interaction import SpeciesInteractionNetwork
from .pollutant_impact import PollutantImpactMap
from .endangered_species import EndangeredSpeciesList

__all__ = [
    "SpeciesInteractionNetwork",
    "PollutantImpactMap",
    "EndangeredSpeciesList",
]
