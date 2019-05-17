# Cat Clicker Premium Pro

Inspired by a famous Facebook trivial game "Cow Clicker" now its time for cats.

The app is a single web page hosted by a Flask app that displays a list of cat names, clicking any name in the list will show the cat's details, clicking the cat's image will increment the click count for the selected cat.

Additionally, pressing the Admin button will show a form where you can edit the cat details name, URL and click count.

The app uses local storage to save data.

## Requirements

The VM comes with all the requirements but off the top of my head you'll need:
  * Python2
  * Flask

## Usage

* Optional: edit the `cats.json` file to your taste (the file comes with 5 preset cat images)

* Run the Vagrant machine and SSH to it

* Run the main app file: `python /vagrant/cat_clicker/views.py &`

* Open "http://localhost:5000/" on browser

* Select cat name and then press on its image to increment its click counter

## Known Issues

* If cat images are not yet cached by the browser, a delay maybe noticed in updating the cat image when selecting different cats

## Room for improvements

* Add styles to the page

## Contributions

I encourage you all to contribute into this simple project to make better and more usable.
