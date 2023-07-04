import os

REALM_NAME = os.environ["REALM_NAME"]
BASE_URL = os.environ["BASE_URL"]
CLIENT_ID = os.environ["CLIENT_ID"]
CLIENT_SECRET = os.environ["CLIENT_SECRET"]
KEYCLOAK_REALM_URL = f"{BASE_URL}/auth/admin/realms/{REALM_NAME}"
KEYCLOAK_USERS_URL = f"{KEYCLOAK_REALM_URL}/users"
KEYCLOAK_GROUPS_URL = f"{KEYCLOAK_REALM_URL}/groups"
KEYCLOAK_AUTH_URL = f"{BASE_URL}/auth/realms/master/protocol/openid-connect/token"

COUPON_GROUPS_MAPPING = {
    "gpu": [
        "gpu-access",
    ],

    "cpu": [
    ],

}
