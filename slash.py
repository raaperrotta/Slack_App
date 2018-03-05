from bottle import run, post, request, response, route
import logging
from math import ceil, inf
import os
import sys
from tabulate import tabulate

log = logging.getLogger('slash_command')

@route('/per_player', method="post")
def per_player():
    response.content_type = 'application/json'
    message_in = request.forms.get("text")

    # TODO: Check time since message was sent to see if Heroku was idling.
    # If we missed the 3 sec timeout window, notify the user and request they try again.

    # If there is an error while processing a caught exception, this is the reply
    package = {"response_type": "ephemeral", "text": "Oops! Something went wrong. Sorry about that."}

    try:
        nums, data, player_max = calc_table(message_in)
        table = format_table(nums, data, player_max)
        # Wrap table in triple ticks so it is displayed fixed-width
        message = '```\n' + table + '\n```'
        package = {"response_type": "in_channel", "text": message}
    except Exception as err:
        log.debug(f'Got error while parsing command: {err}')
        message = f'Could not parse your input. Was it just numbers separated by whitespace (with optional commas)?\n(Error: {err})'
        package = {"response_type": "ephemeral", "text": message}
    finally:
        return package

def calc_table(message_in):
    message_in = message_in.split()
    # Check for player max at end in parentheses
    if message_in[-1][0] == '(' and message_in[-1][-1] == ')':
        player_max = float(message_in.pop()[1:-1])
    else:
        player_max = inf
    # Separate list of numbers by spaces (possibly with comma thousands separators)
    nums = [float(num.replace(',', '')) for num in message_in]
    players = range(2, 11)
    data = [[plrs] + [ceil(pts / plrs) for pts in nums] for plrs in players]
    return nums, data, player_max

def format_table(nums, data, player_max):
    # Replace per_player values that are greater than player max with filler
    data = [[f'{a:,.0f}' if a <= player_max else '-' for a in b] for b in data]
    header = ['Players \ Points'] + [f'{a:,.0f}' for a in nums]
    return tabulate(data, header, stralign='right', tablefmt="psql")

@route('/zillow', method='post')
def link_to_zillow():
    """ Convert address string to hyperlink to zillow listing search.
    When no results are found, link sends user to zillow search results with
    message that no matching home was found. It would be nice if these cases
    could be identified and handled before responding to the user.
    """

    # If there is an error while processing a caught exception, this is the reply
    package = {"response_type": "ephemeral", "text": "Oops! Something went wrong. Sorry about that."}

    try:
        response.content_type = 'application/json'
        address = request.forms.get("text")

        url = 'https://www.zillow.com/homes/'
        url += address.replace(' ', '-').replace(',', '')
        package = {"response_type": "in_channel", "text": url}
    except Exception as err:
        log.debug(f'Got error while parsing command: {err}')
        message = f'Uh-oh! Something went wrong while parsing your input.\n(Error: {err})'
        package = {"response_type": "ephemeral", "text": message}
    finally:
        return package

if __name__ == '__main__':

    # Configure log to print messages to console
    log.setLevel(logging.DEBUG)
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.DEBUG)
    log.addHandler(handler)

    port_config = int(os.getenv('PORT', 5000))
    log.debug(f'Using port {port_config}')
    run(host='0.0.0.0', port=port_config)
