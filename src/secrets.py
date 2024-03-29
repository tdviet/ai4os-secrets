"""
Code snippet for manipulating secrets in AI4OS
"""
import json
import os

import hvac
import jwt

###########################################################################
# Setting environment: server config, access token and home path
# There are different Vault servers for different identity providers
# Comment/uncomment the correct setting according to IdP
###########################################################################

# For authentication with access token from EGI Production Checkin
VAULT_ADDR = "https://vault.services.fedcloud.eu:8200"
VAULT_AUTH_PATH = "jwt"
VAULT_ROLE = ""
VAULT_MOUNT_POINT = "/secrets/"

# For authentication with access token from EGI Development Checkin, uncomment
# the following section
"""
VAULT_ADDR = "https://secrets.services.ai4os.eu:8200"
VAULT_AUTH_PATH = "jwt-egi"
VAULT_ROLE = ""
VAULT_MOUNT_POINT = "/secrets/"
"""

# For authentication with access token from EGI Demo Checkin, uncomment
# the following section
"""
VAULT_ADDR = "https://secrets.services.ai4os.eu:8200"
VAULT_AUTH_PATH = "jwt-egi-demo"
VAULT_ROLE = ""
VAULT_MOUNT_POINT = "/secrets/"
"""

# For authentication with access token from AI4EOSC IAM, uncomment
# the following section
"""
VAULT_ADDR = "https://secrets.services.ai4os.eu:8200"
VAULT_AUTH_PATH = "jwt"
VAULT_ROLE = ""
VAULT_MOUNT_POINT = "/secrets/"
"""

# Get access token from OS environment
access_token = os.getenv("ACCESS_TOKEN")

# Decode the token to get user_id (sub) for home path
try:
    payload = jwt.decode(access_token, options={"verify_signature": False})
    user_id = payload.get("sub")
except (jwt.InvalidTokenError, jwt.ExpiredSignatureError):
    print("Invalid token. Please set valid access token in ACCESS_TOKEN environment variable")
    exit(1)

# Setting home path for secrets. For AI4OS also for EGI Vault deployment,
# the home path is "users/user_id/", where user_id is the sub in access token
home_path = "users/" + user_id + "/"

################################################################################
# End of environment setting. Start the example code of secret manipulation
# Make sure following variables are set:
# VAULT_ADDR (that depends on Identity provider)
# VAULT_AUTH_PATH (that depends on Identity provider)
# VAULT_ROLE (may leave empty)
# VAULT_MOUNT_POINT (should be "/secrets/")
# access_token (for authentication)
# home_path (with sub from access token)
################################################################################

# First of all, init the client
client = hvac.Client(url=VAULT_ADDR)
client.auth.jwt.jwt_login(role=VAULT_ROLE, jwt=access_token, path=VAULT_AUTH_PATH)

# Create/update a secret with name "test01" with key:value {"username":"abcdef", "password":"123456"}
# by calling the corresponding function of the client

print("Creating/updating a secret 'test01'")

client.secrets.kv.v1.create_or_update_secret(
    path=home_path + "test01",
    mount_point=VAULT_MOUNT_POINT,
    secret={"username": "abcdef", "password": "123456"},
)

# Listing secrets in home path. You may list also sub-folder in the home path, just add the sub-folder to the path

print("Listing secrets")

response = client.secrets.kv.v1.list_secrets(
    path=home_path + "",
    mount_point=VAULT_MOUNT_POINT,
)
# Extract the list of secrets in the path from  response
secrets_list = map(str, response["data"]["keys"])

print("\n".join(secrets_list))

# Reading the secret 'test01'

print("Reading the secret 'test01'")

response = client.secrets.kv.v1.read_secret(
    path=home_path + "test01",
    mount_point=VAULT_MOUNT_POINT,
)
# Extract the secret data in dict {key:value} format from response
secret = response["data"]

print(json.dumps(secret))

# Deleting the secret 'test01'
print("Deleting the secret 'test01'")

client.secrets.kv.v1.delete_secret(
    path=home_path + "test01",
    mount_point=VAULT_MOUNT_POINT,
)
