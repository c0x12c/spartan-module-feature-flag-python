import logging

import requests

from feature_flag.core.exceptions import NotifierError
from feature_flag.models.feature_flag import FeatureFlag
from feature_flag.notification.actions import ChangeStatus
from feature_flag.notification.notifier import Notifier

logger = logging.getLogger(__name__)


class SlackNotifier(Notifier):
    def __init__(
        self, slack_webhook_url: str, included_statuses: list[ChangeStatus] = None
    ):
        self.slack_webhook_url = slack_webhook_url
        self.included_statuses = included_statuses

    def send(self, feature_flag: FeatureFlag, change_status: ChangeStatus):
        """
        Sends a Slack notification with details about the given feature flag.

        Args:
            feature_flag (FeatureFlag): The feature flag instance containing name, code, and status information.
            change_status (ChangeStatus): The status of the change for the feature flag.

        Raises:
            requests.exceptions.HTTPError: If the HTTP request to Slack API fails.
            FeatureFlagException: If there is an error sending the notification.
        """

        try:
            if self.included_statuses and change_status not in self.included_statuses:
                return

            message = self._build_message(feature_flag, change_status)
            payload = {"text": message}
            print(f"Sending notification: {message}")
            self._perform_send(payload=payload)
        except requests.exceptions.HTTPError as e:
            raise NotifierError(f"Error sending Slack notification: {e}") from e

    def _perform_send(self, payload: dict):
        response = requests.post(self.slack_webhook_url, json=payload)
        response.raise_for_status()

    @staticmethod
    def _build_message(feature_flag: FeatureFlag, change_status: ChangeStatus) -> str:
        return (
            f"Feature Flag[Code=`{feature_flag.code}`] has been {change_status.value}"
        )
