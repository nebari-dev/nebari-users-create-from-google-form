import logging
import os
import uuid

import requests
import json

REALM_NAME = os.environ["REALM_NAME"]
BASE_URL = os.environ["BASE_URL"]
CLIENT_ID = os.environ["CLIENT_ID"]
CLIENT_SECRET = os.environ["CLIENT_SECRET"]

KEYCLOAK_URL = f"{BASE_URL}/auth/admin/realms/{REALM_NAME}/users"
AUTH_URL = f"{BASE_URL}/auth/realms/master/protocol/openid-connect/token"


def get_access_token():
    auth_data = {
        "grant_type": "client_credentials",
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET
    }
    response = requests.post(AUTH_URL, data=auth_data)
    response_data = response.json()
    access_token = response_data["access_token"]
    return access_token


def create_user(access_token, user_data):
    # Create headers for the API request
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {access_token}"
    }

    # Make the API request to create the user
    response = requests.post(
        KEYCLOAK_URL,
        headers=headers, data=json.dumps(user_data)
    )
    # Check the response status
    if response.status_code == 201:
        logging.info("User created successfully!")
    else:
        logging.info(f"Failed to create user. Status code: {response.status_code}")
        logging.info(f"Response: {response.text}")
    return response


def generate_deterministic_uuid(text, salt="nebari-gh-random"):
    text_ = f"{text}-{salt}"
    return uuid.uuid5(uuid.NAMESPACE_URL, text_).hex


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
    access_token = get_access_token()
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
            create_user(access_token, user_data)
        except Exception as e:
            logging.info(f"Failed to create user: {user}")
            logging.info(e)


if __name__ == "__main__":
    main()
