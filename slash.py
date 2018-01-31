from bottle import run, post, request, response, route
import os
import urllib

@post('/slash/test')
def simple_test():
    return "Hello World"

if __name__ == '__main__':
    port_config = int(os.getenv('PORT', 5000))
    run(host='0.0.0.0', port=port_config)