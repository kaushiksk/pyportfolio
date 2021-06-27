import requests

SCHEME_API_URL = "https://api.mfapi.in/mf/{code}"
session = requests.Session()


def get_scheme_details(amfi_id):
    """
    gets the scheme info for a given scheme code
    :param code: scheme code
    :return: dict or None
    :raises: HTTPError, URLError
    """
    code = str(amfi_id)
    url = SCHEME_API_URL.format(code=code)
    response = session.get(url).json()

    scheme_info = response["meta"]
    if scheme_info:
        scheme_info["nav"] = response["data"][0]["nav"]
        return scheme_info

    return None


if __name__ == "__main__":
    print(get_scheme_details(119551))
    print(get_scheme_details(111))
