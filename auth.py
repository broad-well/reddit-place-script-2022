import requests
from bs4 import BeautifulSoup
import time
import json
import logging

def get_access_token(username, password, logger: logging.Logger):
    while True:
        try:
            logger.debug('Getting access token for ' + username)
            client = requests.Session()
            client.headers.update(
                {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/115.0",
                    "Scheme": "https"
                    
                }
            )

            r = client.get(
                "https://www.reddit.com/login",
            )
            login_get_soup = BeautifulSoup(r.content, "html.parser")
            csrf_token = login_get_soup.find(
                "input", {"name": "csrf_token"}
            )["value"]
            data = {
                "csrf_token": csrf_token,
                "password": password,
                "dest": "https://reddit.com/",
                "username": username,
            }

            r = client.post(
                "https://www.reddit.com/login",
                data=data,
            )
            break
        except Exception:
            logger.error(
                "Failed to connect to websocket, trying again in 30 seconds..."
            )
            time.sleep(30)

    if r.status_code != 200:
        # password is probably invalid
        logger.exception(f"{username} - Authorization failed!")
        logger.debug("response: {r.status_code}, {r.text}", )
        return
    else:
        logger.info(f"{username} - Authorization successful!")
    logger.info("Obtaining access token...")
    r = client.get(
        "https://new.reddit.com/"
    )
    data_str = (
        BeautifulSoup(r.content, features="html.parser")
        .find("script", {"id": "data"})
        .contents[0][len("window.__r = ") : -1]
    )
    data = json.loads(data_str)
    response_data = data["user"]["session"]

    if "error" in response_data:
        logger.info(
            "An error occured. Make sure you have the correct credentials. Response data: {}",
            response_data,
        )
        raise Exception()

    return response_data["accessToken"]