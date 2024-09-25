import unittest
from unittest.mock import patch, MagicMock

import requests

from feature_flag.core.exceptions import NotifierError
from feature_flag.models.feature_flag import FeatureFlag
from feature_flag.notification.change_status import ChangeStatus
from feature_flag.notification.slack_notifier import SlackNotifier


class TestSlackNotifier(unittest.TestCase):

    def setUp(self):
        self.slack_webhook_url = "https://hooks.slack.com/services/T00000000/B00000000/XXXXXXXXXXXXXXXXXXXXXXXX"
        self.feature_flag = FeatureFlag(
            name="Test Feature", code="TEST_FEATURE", enabled=True
        )
        self.change_status = ChangeStatus.ENABLED
        self.notifier = SlackNotifier(self.slack_webhook_url)

    @patch("requests.post")
    def test_send_notification_success(self, mock_post):
        response_mock = MagicMock()
        response_mock.status_code = 200
        mock_post.return_value = response_mock

        self.notifier.send(self.feature_flag, self.change_status)

        mock_post.assert_called_once_with(
            self.slack_webhook_url,
            json={"text": "Feature Flag[Code=`TEST_FEATURE`] has been enabled"},
            headers={},
        )

    @patch("requests.post")
    def test_send_notification_http_error(self, mock_post):
        mock_post.side_effect = requests.exceptions.HTTPError("HTTP error")

        with self.assertRaises(NotifierError) as context:
            self.notifier.send(self.feature_flag, self.change_status)

        self.assertIn("Error sending Slack notification", str(context.exception))

    @patch("requests.post")
    def test_send_notification_excluded_status(self, mock_post):
        self.notifier.excluded_statuses = [self.change_status]

        self.notifier.send(self.feature_flag, self.change_status)

        mock_post.assert_not_called()

    @patch("requests.post")
    def test_send_notification_with_headers(self, mock_post):
        headers = {"Authorization": "Bearer TOKEN"}
        notifier_with_headers = SlackNotifier(self.slack_webhook_url, headers=headers)

        response_mock = MagicMock()
        response_mock.status_code = 200
        mock_post.return_value = response_mock

        notifier_with_headers.send(self.feature_flag, self.change_status)

        mock_post.assert_called_once_with(
            self.slack_webhook_url,
            json={"text": "Feature Flag[Code=`TEST_FEATURE`] has been enabled"},
            headers={"Authorization": "Bearer TOKEN"},
        )


if __name__ == "__main__":
    unittest.main()
