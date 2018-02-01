from bottle import run, post, request, response, route
import logging
from math import ceil
import os
import sys
from tabulate import tabulate

log = logging.getLogger('slash_command')

@route('/per_player', method="post")
def per_player():
    response.content_type = 'application/json'
    message_in = request.forms.get("text")

    try:
        # Separate list of numbers by spaces (possibly with comma tousands separators)
        nums = [float(num.replace(',', '')) for num in message_in.split()]
        players = range(2, 11)
        data = [[plrs] + [ceil(pts / plrs) for pts in nums] for plrs in players]
        data = [[f'{a:,.0f}' for a in b] for b in data]
        header = ['Players \ Points'] + [f'{a:,.0f}' for a in nums]
        table = tabulate(data, header, stralign='right', tablefmt="fancy_grid")
        # Wrap table in triple ticks so it is displayed fixed-width
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
