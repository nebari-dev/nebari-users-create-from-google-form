import logging
import json
import os
import requests

from config import KEYCLOAK_USERS_URL, KEYCLOAK_AUTH_URL, COUPON_GROUPS_MAPPING, SCIPY_COUPON, LAMBDA_AUTH_KEY
from keycloak import KeyCloakClient

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)9s %(lineno)4s %(module)s: %(message)s"
)

logger = logging.getLogger(__name__)
logger.setLevel('INFO')


def create_user(
        username,
        password,
        coupon,
        pyvista,
):
    kclient = KeyCloakClient(realm_url=KEYCLOAK_USERS_URL, auth_url=KEYCLOAK_AUTH_URL)
    print("Inside create_user")
    logger.info("#"*50)
    logger.info(f"## Creating user: {username}")
    logger.info(f"Pass for user: {password}")
    try:
        user_data = {
            "username": username,
            "enabled": True,
            "firstName": username,
            "credentials": [{
                "type": "password",
                "value": password,
                "temporary": False
            }]
        }
        user_id = kclient.create_user(user_data)
        logger.info(f"user_id: {user_id}")
        if user_id and coupon:
            user_groups = COUPON_GROUPS_MAPPING.get('gpu') if pyvista else COUPON_GROUPS_MAPPING.get('cpu')
            logger.info(f"Groups to add the user in: {user_groups}")
            response = kclient.add_user_to_group(user_id, group_names=user_groups)
            logger.info(f"Group add responses: {response}")
            return user_id
    except Exception as e:
        logger.info(f"Failed to create user: {username}")
        logger.info(e)
        raise e


def send_to_slack(message):
    try:
        logger.info(f"Sending message to slack: {message}")
        slack_url = os.environ['SLACK_WEBHOOK_URL']
        logger.info(f"Slack url: {slack_url}")
        headers = {'Content-type': 'application/json'}
        data = {'text': message}
        response = requests.post(slack_url, headers=headers, data=json.dumps(data))
        return response
    except Exception as e:
        logger.error(f"Sending message to slack failed: {e}")



def slack_message(req_id, username, pyvista, msg):
    return f"[`{req_id}`]: {msg} | username: {username}, pyvista: {pyvista}",


def handler(event, context):
    print("Setting up logging")
    body = json.loads(event['body'])
    req_id = context.aws_request_id[:7]

    # There is a better way to do it, but this is just
    # a quick way to check if the request is coming from
    # a trusted source.
    if body.get('auth_key') != LAMBDA_AUTH_KEY:
        error = "Authentication key mismatch"
        return {
            "error": error
        }

    username = body['username']
    password = body['password']
    coupon: str = body['coupon']
    pyvista = body['pyvista']
    logger.info(body)
    if coupon and coupon.lower() == SCIPY_COUPON:
        slack_msg = slack_message(req_id, username, password, msg="⚙️ User creation started!")
        send_to_slack(slack_msg)
        try:
            user_id = create_user(username, password, coupon, pyvista)
        except Exception as e:
            slack_msg = slack_message(req_id, username, password, msg=f"❌ ERROR FATAL `{e}`")
            send_to_slack(slack_msg)
            raise e
        slack_msg = slack_message(req_id, username, password, msg=f"✅ User creation complete! user_id: {user_id}")
        send_to_slack(slack_msg)
    else:
        slack_msg = slack_message(req_id, username, password, msg=f"🚫 ERROR! Invalid Coupon: {coupon}")
        send_to_slack(slack_msg)
        msg = f"Invalid coupon code: {coupon}"
        logger.info(msg)
        return {
            "message": msg
        }
    return {
        "status": "ok",
    }

