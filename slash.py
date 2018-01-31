from bottle import run, post, request, response, route
import logging
import os
import sys
import urllib

log = logging.getLogger('slash_command')

@post('/test')
def test():
    log.debug('Hello, World!')
    return "Hello World"

@route('/per_player', method="post")
def per_player():
    response.content_type = 'application/json'
    postdata = request.forms.get("text")


    try:
        # Separate list of numbers by spaces
        nums = command.split()
        nums = [int(num) for num in nums]

        message = '```\n'
        w = 9  # column width in characters
        message += ' ' * w  # add empty top left corner
        # Add column headers with number of points
        for num in nums:
            message += f'{num:>{w},.0f}'
        for num_players in range(2, 10):
            message += f'\n{num_players:>{w}d}'
            for num in nums:
                per_player = (num + num_players - 1) // num_players  # ceil
                message += f'{per_player:>{w},.0f}'
        message += '\n```'

        message = 'Hello, World!'
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
