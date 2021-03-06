import json
import random
from celery import decorators
import requests
from requests.api import request
from celery.utils.log import get_logger
from config import Config
from circuitbreaker import circuit

logger = get_logger(__name__)

_APP = None

config = Config()
USER_MS = config.USERS_MS_URL
MESSAGE_MS = config.MESSAGE_MS_URL
SEND_NOTIFICATION_MS = config.NOTIFICATIONS_MS_URL


@decorators.task(name="mib.tasks.periodic_tasks.check_messages")
@circuit(expected_exception=requests.RequestException)
def check_messages(test_mode):
    """Check that messages have been sent correctly

    :param test_mode: determine the operating mode
    :type test_mode: bool
    :raises Exception: if an error occurs
    :returns: state of execution and number of messages sent
    :rtype: couple (bool,int)
    """
    global _APP
    # lazy init
    if _APP is None:
        from mib import create_app

        app = create_app()
    else:
        app = _APP
    logger.info("Start check_message test_mode: " + str(test_mode))
    result = False
    with app.app_context():
        try:
            # getting unsent messages
            reply = requests.get(MESSAGE_MS + "message/unsent")
            if reply.status_code == 200:
                messages = reply.json()
                # for each message has been found as undelivered send notification
                for msg in messages:
                    reply = requests.put(
                        MESSAGE_MS + "message",
                        json={
                            "attribute": "is_delivered",
                            "message_id": msg["id"],
                            "value": True,
                        },
                    )
                    if reply.status_code == 200:
                        recipient = msg["recipient"]
                        sender = msg["sender"]
                        # getting emails
                        reply_r = requests.get(USER_MS + f"user/{recipient}/email")
                        reply_s = requests.get(USER_MS + f"user/{sender}/email")
                        if reply_r.status_code == 200:
                            email_r = reply_r.json()["email"]
                            email_s = (
                                reply_s.json()["email"]
                                if reply_s.status_code == 200
                                else "mib@mibmail.it"
                            )
                            # send notification via email microservice
                            _send_email(
                                email_s, email_r, "You have just received a message!"
                            )
            else:
                messages = []
            result = True
        except Exception as e:
            logger.exception("check_messages raises ", e)
            raise e
    # state and number of sent messages
    couple = (result, len(messages))
    logger.info("End check_message couple: " + str(couple))
    return couple


@decorators.task(name="mib.tasks.periodic_tasks.lottery")
@circuit(expected_exception=requests.RequestException)
def lottery(test_mode):
    """implement lottery game
    :param test_mode : determine the operating mode
    :type test_mode: bool
    :returns: False in case errors occur otherwise True
    :rtype: bool
    """
    logger.info("Lottery game start")
    global _APP
    result = False
    id_winner = -1
    # lazy init
    if _APP is None:
        from mib import create_app

        app = create_app()
    else:
        app = _APP

    with app.app_context():
        # get all participants
        reply = requests.get(USER_MS + "user/list/public")
        if reply.status_code == 200:
            participants = reply.json()
            # extract the winner randomly
            winner = random.randint(0, len(participants) - 1)
            email_r = participants[winner]["email"]
            sender = "mib@mibmail.it"
            id_winner = participants[winner]["id"]
            # add points
            reply = requests.put(
                USER_MS + f"user/points/{id_winner}", json={"points": 60}
            )
            _send_email(sender, email_r, "You have just won 60 point!")
            result = True

    logger.info("Lottery game end winner id: " + str(id_winner))
    return (result, id_winner)

@circuit(expected_exception=requests.RequestException)
def _send_email(email_s, email_r, body):
    # send notification via email microservice
    requests.put(
        SEND_NOTIFICATION_MS + "email",
        json={
            "sender": email_s,
            "recipient": email_r,
            "body": body,
        },
    )
