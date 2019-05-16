# Cat Clicker

Inspired by a famous Facebook game called "Cow Clicker" this is Cat Clicker.

It's a single HTML page hosted by a Flask app where you select one of the cats available in the list and clicking on the cat image a click counter is incremented per cat.

## Requirements

The VM comes with all the requirements but off the top of my head you'll need:
  * Python2
  * Flask
  * SQLAlchemy
  * Redis DB Server

## Usage

* The app comes with a preset list of cats in the file "cats.json" but of course you can modify this file and it reflects on the page

* Run the Vagrant machine and SSH to it

* Run the main app file: `python /vagrant/cat_clicker/views.py &`

* Open "http://localhost:5000/" on browser

## Known Issues

* The counter are rest upon refresh

## Room for improvements

* Adding styles to the page

## Contributions

I encourage you all to contribute into this simple project to make better and more usable.