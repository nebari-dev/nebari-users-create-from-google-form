import logging
import json

from config import KEYCLOAK_USERS_URL, KEYCLOAK_AUTH_URL, COUPON_GROUPS_MAPPING, SCIPY_COUPON
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
            user_groups = COUPON_GROUPS_MAPPING.get('gpu') if pyvista else COUPON_GROUPS_MAPPING.get('gpu')
            logger.info(f"Groups to add the user in: {user_groups}")
            response = kclient.add_user_to_group(user_id, group_names=user_groups)
            logger.info(f"Group add responses: {response}")
    except Exception as e:
        logger.info(f"Failed to create user: {username}")
        logger.info(e)
        raise e


def handler(event, context):
    print("Setting up logging")
    body = json.loads(event['body'])
    username = body['username']
    password = body['password']
    coupon: str = body['coupon']
    pyvista = body['pyvista']
    logger.info(body)
    if coupon and coupon.lower() == SCIPY_COUPON:
        create_user(username, password, coupon, pyvista)
    else:
        return {
            "message": f"Invalid coupon code: {coupon}"
        }
    return {
        "status": "ok",
        "body": body
    }

