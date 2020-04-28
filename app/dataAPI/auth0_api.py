import http.client
import json


def getAuth0AppToken(client, secret):
    try:
        conn = http.client.HTTPSConnection("oakypokey.auth0.com")
        payload = "{\"client_id\":\"" + str(client) + "\",\"client_secret\":\"" + str(
            secret) + "\",\"audience\":\"https://oakypokey.auth0.com/api/v2/\",\"grant_type\":\"client_credentials\"}"

        headers = {'content-type': "application/json"}

        conn.request("POST", "/oauth/token", payload, headers)

        res = conn.getresponse()
        data = res.read()

        return {"error": False, "data": data.decode("utf-8")}

    except Exception as e:
        return {"error": True, "message": e}


def getAuth0UserData(token, user_id):
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
