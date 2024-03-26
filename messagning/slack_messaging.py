import configparser

# Create a ConfigParser object
config = configparser.ConfigParser()
# Read the configuration file
config.read('../secretes/config.ini')

# Access values using sections and keys
token = config['SLACK']['token']

from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from helper.logger import logger


def send_message(message, channel):
    client = WebClient(token=token)
    try:
        # Replace 'CHANNEL_ID' with the ID of the channel or user you want to send the message to
        response = client.chat_postMessage(
            channel=channel,
            text=message
        )
        logger.debug("Message sent successfully!")
    except SlackApiError as e:
        logger.error(f"Error sending message: {e.response['error']}")
