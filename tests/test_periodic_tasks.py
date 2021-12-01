import unittest
import responses

from datetime import datetime
from mib.tasks.periodic_tasks import lottery, check_messages


class TestMessages(unittest.TestCase):
    def setUp(self):
        from mib.tasks.periodic_tasks import USER_MS, SEND_NOTIFICATION_MS, MESSAGE_MS

        self.user_service_endpoint = USER_MS
        self.send_notfication_endpoint = SEND_NOTIFICATION_MS
        self.message_service_endpoint = MESSAGE_MS

    @responses.activate
    def test_lottery_tasks(self):
        # mock getting partecipants
        responses.add(
            responses.GET,
            self.user_service_endpoint + "user/list/public",
            json=[
                {"email": "recipient@example.com", "id": 1},
                {"email": "recipient@example.com", "id": 2},
            ],
            status=200,
        )
        # both users could win
        responses.add(
            responses.PUT,
            url=self.user_service_endpoint + "user/points/" + str(2),
            status=200,
        )
        responses.add(
            responses.PUT,
            url=self.user_service_endpoint + "user/points/" + str(1),
            status=200,
        )
        # mock email notification
        responses.add(
            responses.PUT,
            url=self.send_notfication_endpoint + "email",
            status=200,
        )
        # call task
        (state, id_winner) = lottery(True)
        assert state and id_winner in [1, 2]

    @responses.activate
    def test_check_message(self):
        responses.add(
            responses.GET,
            self.message_service_endpoint + "message/unsent",
            json=[
                {"recipient": 1, "id": 1, "sender": 2},
                {"recipient": 2, "id": 1, "sender": 1},
            ],
            status=200,
        )
        responses.add(
            responses.PUT,
            url=self.message_service_endpoint + "message",
            status=200,
        )
        responses.add(
            responses.GET,
            url=self.user_service_endpoint + f"user/{1}/email",
            json={"email": "recipient@example.com"},
        )
        responses.add(
            responses.GET,
            url=self.user_service_endpoint + f"user/{2}/email",
            json={"email": "recipient@example.com"},
        )
        # mock email notification
        responses.add(
            responses.PUT,
            url=self.send_notfication_endpoint + "email",
            status=200,
        )

        (result, messages_number) = check_messages(True)

        assert result and messages_number == 2
