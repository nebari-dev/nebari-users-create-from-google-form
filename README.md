# Nebari user's from Google Form (WIP)

This will create users in Nebari using Keycloak's API.

The information flow is like the following:

1. User fills in Google Form
2. Google App's Script listens to form submission and sends the form data to this repository into `users.json`
3. On any push to the repository GitHub Actions will run the python script which will call Keycloak's API to add users to the Nebari Deployment
