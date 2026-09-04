from abc import ABC, abstractmethod


class BaseSource(ABC):

    name = "base"

    def __init__(
        self,
        config,
        timezone
    ):

        self.config = config
        self.timezone = timezone

    @abstractmethod
    def fetch(self, channel, date):

        raise NotImplementedError