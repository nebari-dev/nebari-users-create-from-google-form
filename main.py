import os

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
        print("User created successfully!")
    else:
        print("Failed to create user. Status code:", response.status_code)
        print("Response:", response.text)
    return response


def main():
    access_token = get_access_token()
    # User data
    user_data = {
        "username": "new_user",
        "email": "new_user@example.com",
        "enabled": True,
        "firstName": "John",
        "lastName": "Doe",
        "credentials": [{
            "type": "password",
            "value": "password",
            "temporary": False
        }]
    }
    return create_user(access_token, user_data)


if __name__ == "__main__":
    main()
