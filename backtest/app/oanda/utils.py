"""Definition of decorator."""


def endpoint(url: str):
    """Specify the endpoint of the api-server.
    Args:
        url (str): The path to add below the hostname.
        method (str): Specify the HTTP method.
    """
    def deco(obj):
        obj.ENDPOINT = url
        # obj.METHOD = method
        # obj.EXPECTED_STATUS = method
        return obj
    return deco
