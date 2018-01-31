import logging
from logging.handlers import SysLogHandler
import os
import sys
import time
import re
from slackclient import SlackClient

log = logging.getLogger('starterbot')

# instantiate Slack client
slack_client = SlackClient(os.environ.get('SLACK_API_TOKEN'))
# starterbot's user ID in Slack: value is assigned after the bot starts up
starterbot_id = None

# constants
rtm_read_delay = 1 # 1 second delay between reading from RTM
command_word = "do"
mention_regex = re.compile("^<@(|[WU].+?)>(.*)")

def parse_bot_commands(slack_events):
    """
        Parses a list of events coming from the Slack RTM API to find bot commands.
        If a bot command is found, this function returns a tuple of command and channel.
        If its not found, then this function returns None, None.
    """
    for event in slack_events:
        # Print just the type for annoyingly long events
        if event['type'] in {'desktop_notification'}:
            log.debug(f'Heard event type {event["type"]}.')
        else:
            log.debug(f'Heard event {event}.')
        if event["type"] == "message" and not "subtype" in event:
            user_id, message = parse_direct_mention(event["text"])
            if user_id == starterbot_id:
                return message, event["channel"]
    return None, None

def parse_direct_mention(message_text):
    """
        Finds a direct mention (a mention that is at the beginning) in message text
        and returns the user ID which was mentioned. If there is no direct mention, returns None
    """
    matches = mention_regex.search(message_text)
    # the first group contains the username, the second group contains the remaining message
    return (matches.group(1), matches.group(2).strip()) if matches else (None, None)

def handle_command(command, channel):
    """
        Executes bot command if the command is known
    """

    def reply(response):
        # Sends the response back to the channel
        slack_client.api_call("chat.postMessage", channel=channel, text=response)

    try:
        # Separate list of numbers by spaces
        nums = command.split()
        nums = [int(num) for num in nums]
    except Exception as err:
        log.debug(f'Got error while parsing command: {err}')
        reply("I don't understand. Did you input a list of numbers?")
        return

    response = '```\n'
    w = 9  # column width in characters
    response += ' ' * w  # add empty top left corner
    # Add column headers with number of points
    for num in nums:
        response += f'{num:>{w},.0f}'
    for num_players in range(2, 10):
        response += f'\n{num_players:>{w}d}'
        for num in nums:
            per_player = (num + num_players - 1) // num_players  # ceil
            response += f'{per_player:>{w},.0f}'
    response += '\n```'
    reply(response)

if __name__ == "__main__":

    # Configure log to print messages to console
    log.setLevel(logging.DEBUG)
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    log.addHandler(handler)
    
    # Add log handler for Heroku -> PaperTrail
    handler = SysLogHandler()
    handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    log.addHandler(handler)

    log.debug('Attempting to login to Slack.')
    if slack_client.rtm_connect(with_team_state=False):
        log.debug("Starter Bot connected and running!")
        # Read bot's user ID by calling Web API method `auth.test`
        starterbot_id = slack_client.api_call("auth.test")["user_id"]
        log.debug(f'Connected with id {starterbot_id}. Entering parse loop.')
        while True:
            command, channel = parse_bot_commands(slack_client.rtm_read())
            if command:
                log.debug(f'Heard command "{command}".')
                handle_command(command, channel)
            time.sleep(rtm_read_delay)
    else:
        log.debug("Connection failed. Exception traceback printed above.")
