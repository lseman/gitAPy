import requests
# send discord webhook
def send_webook(message, url):
    """
    Sends a message to a Discord webhook.

    Args:
        message (str): The message to send.
        url (str): The webhook URL.

    Returns:
        None
    """
    data = {"content": message}
    requests.post(url, json=data)
