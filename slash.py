from bottle import run, post, request, response, route
import logging
import os
import sys
from tabulate import tabulate

log = logging.getLogger('slash_command')

@post('/test')
def test():
    log.debug('Hello, World!')
    return "Hello World"

@route('/per_player', method="post")
def per_player():
    response.content_type = 'application/json'
    message_in = request.forms.get("text")

    try:
        # Separate list of numbers by spaces (possibly with comma tousands separators)
        nums = [int(num.replace(',', '')) for num in message_in.split()]
        players = range(1, 11)
        data = [[(pts + plrs - 1) // plrs for plrs in players] for pts in nums]
        data = [[f'{a:,.0f}' for a in b] for b in data]
        table = tabulate(data, players, stralign='right')
        message = '```\n' + table + '\n```'
        package = {"response_type": "in_channel", "text": message}
    except Exception as err:
        log.debug(f'Got error while parsing command: {err}')
        message = f'Could not parse your input. Was it just numbers separated by whitespace?\n(Error: {err})'
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
