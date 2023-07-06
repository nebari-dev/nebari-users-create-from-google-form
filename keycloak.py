import logging
import uuid

import requests
import json

from config import CLIENT_ID, CLIENT_SECRET, KEYCLOAK_USERS_URL, KEYCLOAK_GROUPS_URL

logger = logging.getLogger(__name__)
logger.setLevel('INFO')


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
        return {user['username']: user for user in rjson}

    def add_user_to_group(self, user_id, group_names):
        groups = self.get_groups()
        group_ids = {groups[group_name]['id'] for group_name in group_names}
        logger.info(f"Adding user {user_id} to groups: {group_names}")
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
            logger.info(f"Adding user to group {group_add_url.split('/')[-1]} response: {response}")
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
            headers=headers,
            data=json.dumps(user_data)
        )
        user_id = None
        if response.status_code == 201:
            logger.info("User created successfully!")
            user_id = response.headers["Location"].split("/")[-1]

        elif response.status_code == 409:
            logger.info(f"User already exists: {user_data['username']} {response.status_code}")
            users = self.get_users()
            user_id = users[user_data['username']]['id']
        else:
            logger.info(f"Failed to create user. Status code: {response.status_code}")
            logger.info(f"Response: {response.text}")
        return user_id
