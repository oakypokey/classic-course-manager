import http.client
import json


def getAuth0AppToken(client, secret):
    """Get Auth0 Management API token for Auth0 account

    Args:
        client (string): client_id for Auth0
        secret (string): client_secret for Auth0

    Returns:
        dict: information about whether or not the request was successful and the token itself

    Source:
        https://auth0.com/docs/quickstart/backend/python/02-using
    """
    try:
        conn = http.client.HTTPSConnection("oakypokey.auth0.com")
        payload = "{\"client_id\":\"" + str(client) + "\",\"client_secret\":\"" + str(
            secret) + "\",\"audience\":\"https://oakypokey.auth0.com/api/v2/\",\"grant_type\":\"client_credentials\"}"

        headers = {'Content-Type': "application/json"}

        conn.request("POST", "/oauth/token", payload, headers)

        res = conn.getresponse()
        data = res.read()

        return {"error": False, "data": data.decode("utf-8")}

    except Exception as e:
        return {"error": True, "message": e}


def getAuth0UserData(token, user_id):
    """Get's the users data that is store in Auth0

    Args:
        token (dict): Auth0 Management token dict
        user_id (string): user ID for the user whose information is being retrived

    Returns:
        dict: whether or not an error occured and all the users data including google-idap

    Source:
        https://auth0.com/docs/quickstart/backend/python/02-using
    """

    try:
        token_dict = json.loads(token)
        conn = http.client.HTTPSConnection("oakypokey.auth0.com")

        headers = {'authorization': str(
            token_dict["token_type"]) + " " + str(token_dict["access_token"])}

        conn.request(
            "GET",
            "/api/v2/users/" +
            str(user_id).replace(
                "|",
                "%7C"),
            headers=headers)

        res = conn.getresponse()
        data = res.read()

        return {"error": False, "data": json.loads(data.decode("utf-8"))}
    except Exception as e:
        print("getIDAPToken: " + e)
        return {"error": True, "message": e}
