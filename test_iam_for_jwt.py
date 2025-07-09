"""
Module for requesting and verifying OAuth2 JWT tokens from Oracle IDCS.

Classes:
    OCIJWTClient: Fetches access tokens using client credentials flow.
    OCIJWTServer: Decodes and verifies JWT signatures using IDCS JWKS.
"""

import base64
import requests
import oci
import jwt
from jwt import PyJWKClient
from utils import get_console_logger
from config import DEBUG
from config_private import OCI_CLIENT_ID

logger = get_console_logger()


class OCIJWTClient:
    """
    Client for obtaining JWT access tokens from Oracle Identity Cloud Service (IDCS)
    via the OAuth2 client credentials grant.

    Attributes:
        base_url (str): Base URL for the IDCS tenant.
        scope (str): OAuth2 scope to include in the token request.
        client_id (str): OCI client ID (from config).
        client_secret (str): OCI client secret (from config).
        token_url (str): Full URL for the token endpoint.

    Methods:
        get_token() -> Tuple[str, str, int]:
            Requests a token and returns (access_token, token_type, expires_in).
    """

    def __init__(self, base_url, scope, secret_ocid):
        """
        Initializes the token client.

        Args:
            base_url: The base URL of the IDCS tenant.
            scope: The requested OAuth2 scope.
            secret_ocid: the ocid of the secret in the vault
        """
        self.base_url = base_url
        self.scope = scope
        self.token_url = f"{self.base_url}/oauth2/v1/token"
        self.client_id = OCI_CLIENT_ID
        self.client_secret = self.get_client_secret(secret_ocid)
        self.timeout = 60

    def get_client_secret(self, secret_ocid: str):
        """
        Read the client secret from OCI vault
        """
        config = oci.config.from_file()
        secrets_client = oci.secrets.SecretsClient(config)

        # Retrieve the current secret bundle
        response = secrets_client.get_secret_bundle(secret_id=secret_ocid)
        b64 = response.data.secret_bundle_content.content

        # Decode and use
        secret_value = base64.b64decode(b64).decode("utf-8")
        return secret_value

    def get_token(self):
        """
        Requests a client_credentials access token from IDCS.

        Returns:
            Tuple of access token (str), token type (str), and expiration (int seconds).

        Raises:
            HTTPError if the request fails.
        """
        data = {"grant_type": "client_credentials", "scope": self.scope}
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        response = requests.post(
            self.token_url,
            data=data,
            headers=headers,
            auth=(self.client_id, self.client_secret),
            timeout=self.timeout,
        )

        if DEBUG:
            logger.info("---- HTTP response text ----")
            logger.info(response.text)

        # check for any error
        response.raise_for_status()

        token_data = response.json()

        return (
            token_data["access_token"],
            token_data["token_type"],
            token_data["expires_in"],
        )


class OCIJWTServer:
    """
    Server-side utility for decoding and verifying JWT tokens using
    the JWKS endpoint of Oracle IDCS.

    Attributes:
        jwks_url (str): URL to fetch JWKS (JSON Web Key Set).
        audience (str): Expected audience claim in the token.
        issuer (str): Expected issuer claim in the token.

    Methods:
        decode_unverified(token: str) -> dict:
            Returns unverified claims for inspection/debug.
        verify_token(token: str) -> dict:
            Fully validates the token signature and claims.
    """

    def __init__(self, base_url, audience, issuer):
        """
        Initializes the verifier.

        Args:
            base_url: Base URL for the IDCS tenant.
            audience: Expected 'aud' claim in JWT.
            issuer: Expected 'iss' claim in JWT.
        """
        self.jwks_url = f"{base_url}/admin/v1/SigningCert/jwk"
        self.audience = audience
        self.issuer = issuer

    def decode_unverified(self, _token):
        """
        Decodes a JWT without verifying the signature.

        Args:
            token: The JWT string.

        Returns:
            Dictionary of JWT claims.
        """
        return jwt.decode(_token, options={"verify_signature": False})

    def verify_token(self, _token):
        """
        Verifies a JWT's signature and standard claims using JWKS.

        Args:
            token: The JWT string.

        Returns:
            Dictionary of verified JWT claims.

        Raises:
            jwt.exceptions.PyJWKClientError, jwt.PyJWTError if verification fails.
        """
        logger.info("Getting public key from OCI IAM...")
        jwks_client = PyJWKClient(self.jwks_url)
        signing_key = jwks_client.get_signing_key_from_jwt(_token).key

        logger.info("Verifying token...")
        return jwt.decode(
            _token,
            signing_key,
            # this is the default for OCI iam
            algorithms=["RS256"],
            audience=self.audience,
            issuer=self.issuer,
            verify=True,
        )


#
# Main
#
BASE_URL = "https://idcs-930d7b2ea2cb46049963ecba3049f509.identity.oraclecloud.com"
# this is the scope forwhich the token is issued
SCOPE = "urn:opc:idm:__myscopes__"
# these are used in verification
# these is depending from the tenant
# the ocid of the secret in the vault
SECRET_OCID = "ocid1.vaultsecret.oc1.eu-frankfurt-1.amaaaaaa2xxap7yalre4qru4asevgtxlmn7hwh27awnzmdcrnmsfqu7cia7a"

AUDIENCE = "urn:opc:lbaas:logicalguid=idcs-930d7b2ea2cb46049963ecba3049f509"
ISSUER = "https://identity.oraclecloud.com/"

client = OCIJWTClient(BASE_URL, SCOPE, SECRET_OCID)
print("")
print("Getting token from OCI IAM...")
token, token_type, expires_in = client.get_token()
print(token)
print("Token type:", token_type)

server = OCIJWTServer(BASE_URL, AUDIENCE, ISSUER)
claims = server.decode_unverified(token)
print("")
print("Unverified claims:", claims)
print("")

verified = server.verify_token(token)
print("")
print("Token Verification OK:", verified)
