"""DAG Factory."""

from abc import ABC, abstractmethod

from .enums import EnvironmentName


class CreatorDAG(ABC):
    """Abstract DAG creator class."""

    def __init__(self, environment: EnvironmentName):
        """Initialize the creator.

        Args:
            environment (EnvironmentName): The environment name
        """
        self.environment = environment

    @abstractmethod
    def create(self):
        """Abstract create method."""
        pass
