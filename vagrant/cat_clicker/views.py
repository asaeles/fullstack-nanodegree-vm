#!/usr/bin/env python2

from flask import (Flask, g, render_template, send_from_directory)
from werkzeug.routing import BaseConverter

# Initialize application objects
app = Flask(__name__)


class RegexConverter(BaseConverter):
    """RegEx class extending base converter
    adding regular expression support."""

    def __init__(self, url_map, *items):
        super(RegexConverter, self).__init__(url_map)
        self.regex = items[0]


# Add new RegEx converter class to URL Mapping for routes
app.url_map.converters['regex'] = RegexConverter


# Home page
@app.route('/')
def start():
    """Display home page"""
    return render_template('app.html')


# Resources
@app.route(r'/<regex("[^\.]+(\.(html|css|js|ico|json))?"):path>')
def send_stuff(path):
    """Generic route to fetch any resources
    required by HTML page, route is limited
    by regular expressions"""
    return send_from_directory('templates', path)


# Finally application start if file is run as main
if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
