#!/usr/bin/env python2

from flask import Flask, render_template, send_from_directory
from werkzeug.routing import BaseConverter

# Initialize application objects
app = Flask(__name__)

# Add RegEx converter to URL Mapping for routes
class RegexConverter(BaseConverter):
    def __init__(self, url_map, *items):
        super(RegexConverter, self).__init__(url_map)
        self.regex = items[0]


app.url_map.converters['regex'] = RegexConverter

# Home page
@app.route('/')
def start():
    return render_template('app.html')

# Resources
@app.route('/<regex("[^\.]+(\.(html|css|js|ico|json))?"):path>')
def send_stuff(path):
    return send_from_directory('templates', path)


# Finally application start if file is run as main
if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
