import logging
import os
import uuid

import requests
import json

REALM_NAME = os.environ["REALM_NAME"]
BASE_URL = os.environ["BASE_URL"]
CLIENT_ID = os.environ["CLIENT_ID"]
CLIENT_SECRET = os.environ["CLIENT_SECRET"]

KEYCLOAK_REALM_URL = f"{BASE_URL}/auth/admin/realms/{REALM_NAME}"
KEYCLOAK_USERS_URL = f"{KEYCLOAK_REALM_URL}/users"
KEYCLOAK_GROUPS_URL = f"{KEYCLOAK_REALM_URL}/groups"

KEYCLOAK_AUTH_URL = f"{BASE_URL}/auth/realms/master/protocol/openid-connect/token"

GROUP_NAMES = [
    "amit-test-1",
    "amit-test-2",
]


def generate_deterministic_uuid(text, salt="nebari-gh-random"):
    text_ = f"{text}-{salt}"
    return uuid.uuid5(uuid.NAMESPACE_URL, text_).hex


class KeyCloakClient:
    def __init__(self, realm_url, auth_url):
        self.realm_url = realm_url
        self.auth_url = auth_url

    def get_access_token(self):
        auth_data = {
            "grant_type": "client_credentials",
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET
        }
        response = requests.post(self.auth_url, data=auth_data)
        response_data = response.json()
        access_token = response_data["access_token"]
        return access_token

    def get_groups(self):
        response = requests.get(
            KEYCLOAK_GROUPS_URL,
            headers=self._create_headers(),
        )
        rjson = response.json()
        return {group['name']: group for group in rjson}

    def get_users(self):
        response = requests.get(
            KEYCLOAK_USERS_URL,
            headers=self._create_headers(),
        )
        rjson = response.json()
        return {user['email']: user for user in rjson}

    def add_user_to_group(self, user_id, group_names):
        groups = self.get_groups()
        group_ids = {groups[group_name]['id'] for group_name in group_names}
        logging.info(f"Adding user {user_id} to groups: {group_names}")
        group_add_urls = {
            f"{KEYCLOAK_USERS_URL}/{user_id}/groups/{group_id}"
            for group_id in group_ids
        }
        responses = []
        for group_add_url in group_add_urls:
            response = requests.put(
                group_add_url,
                headers=self._create_headers(),
            )
            responses.append(response)
            logging.info(f"Adding user to group {group_add_url.split('/')[-1]} response: {response}")
        return responses

    def _create_headers(self, access_token=None):
        if not access_token:
            access_token = self.get_access_token()
        return {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {access_token}"
        }

    def create_user(self, user_data):
        headers = self._create_headers()
        response = requests.post(
            self.realm_url,
            headers=headers, data=json.dumps(user_data)
        )
        user_id = None
        if response.status_code == 201:
            logging.info("User created successfully!")
            user_id = response.headers["Location"].split("/")[-1]

        if response.status_code == 409:
            logging.info(f"User already exists: {user_data['email']} {response.status_code}")
            users = self.get_users()
            user_id = users[user_data['email']]['id']
        else:
            logging.info(f"Failed to create user. Status code: {response.status_code}")
            logging.info(f"Response: {response.text}")
        return user_id


def setup_logging():
    """
    Setups the logging.
    :return: None
    """
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)9s %(lineno)4s %(module)s: %(message)s"
    )


def main():
    setup_logging()
    kclient = KeyCloakClient(realm_url=KEYCLOAK_USERS_URL, auth_url=KEYCLOAK_AUTH_URL)
    users = json.load(open('users.json', 'r'))
    total_users = len(users)
    for idx, user in enumerate(users):
        logging.info("#"*50)
        logging.info(f"## {idx + 1}/{total_users} Creating user: {user}")
        password = generate_deterministic_uuid(user['Email'])
        logging.info(f"Pass for user: {password}")
        try:
            user_data = {
                "username": user['Email'],
                "email": user['Email'],
                "enabled": True,
                "firstName": user["Name"],
                "credentials": [{
                    "type": "password",
                    "value": password,
                    "temporary": False
                }]
            }
            user_id = kclient.create_user(user_data)
            if user_id:
                response = kclient.add_user_to_group(user_id, group_names=GROUP_NAMES)
                logging.info(f"Group add responses: {response}")
        except Exception as e:
            logging.info(f"Failed to create user: {user}")
            logging.info(e)
            raise e


if __name__ == "__main__":
    main()
