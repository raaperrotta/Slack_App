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
    postdata = request.forms.get("text")
    message = 'Hello, World!'
    package = {"response_type": "in_channel", "text": message}
    response.content_type = 'application/json'
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
