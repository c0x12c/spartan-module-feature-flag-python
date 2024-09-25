from abc import ABC, abstractmethod

from feature_flag.models.feature_flag import FeatureFlag
from feature_flag.notification.change_status import ChangeStatus


class Notifier(ABC):
    @abstractmethod
    def send(self, feature_flag: FeatureFlag, change_status: ChangeStatus):
        pass
