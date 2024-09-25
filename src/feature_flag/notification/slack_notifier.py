import logging

import requests

from feature_flag.core.exceptions import NotifierError
from feature_flag.models.feature_flag import FeatureFlag
from feature_flag.notification.actions import ChangeStatus
from feature_flag.notification.notifier import Notifier

logger = logging.getLogger(__name__)


class SlackNotifier(Notifier):
    def __init__(
        self, slack_webhook_url: str, excluded_statuses: list[ChangeStatus] = None
    ):
        self.slack_webhook_url = slack_webhook_url
        self.excluded_statuses = excluded_statuses

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
            logger.debug(
                f"Sending notification for feature flag with [code={feature_flag.code}, changeStatus={change_status}]"
            )
            if self.excluded_statuses and change_status in self.excluded_statuses:
                logger.debug(
                    f"ChangeStatus {change_status} is in the excluded statuses list; notification will not be sent."
                )
                return

            message = self._build_message(feature_flag, change_status)
            payload = {"text": message}
            self._perform_send(payload=payload)
            logger.debug(
                f"Notification for feature flag with [code={feature_flag.code}, changeStatus={change_status}] sent successfully"
            )
        except Exception as e:
            raise NotifierError(f"Error sending Slack notification: {e}") from e

    def _perform_send(self, payload: dict):
        response = requests.post(self.slack_webhook_url, json=payload)
        response.raise_for_status()

    @staticmethod
    def _build_message(feature_flag: FeatureFlag, change_status: ChangeStatus) -> str:
        return (
            f"Feature Flag[Code=`{feature_flag.code}`] has been {change_status.value}"
        )
