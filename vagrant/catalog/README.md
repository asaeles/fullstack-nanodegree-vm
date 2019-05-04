# Catalog Manager

A Single Page App (SPA) website complete front-end and back-end based on Flask and SQLAlchemy for cataloging stuff.

The website allows any logged in user to add categories and add sub-items under these categories and also edit and delete categories and items.

O-Auth login using Google is supported.

## Requirements

The VM comes with all the requirements but off the top of my head you'll need:
  * Python2
  * Flask
  * SQLAlchemy
  * Redis DB Server

## Usage

* For Google O-Auth to work you must:
  1. Edit `templates/app.html` and put your client id under the content of the `meta` tag wit the name `google-signin-client_id`
  2. Save your application's `client_secrets.json` beside `views.py`

* Run the Vagrant machine and SSH to it

* Run the Redis DB Server: `redis-server &`

* Run the main app file: `python /vagrant/catalog/views.py &`

* Open "http://localhost:5000/" on browser

## Known Issues

* Pressing edit or delete category buttons will toggle the collapse of the category
* After any edit to the catalog it will collapse all categories

## Room for improvements

* Add the ability for users to change password and upload their photo
* Add the ability to add photo and description for categories and items
* Enhance the loading screen

## Contributions

I encourage you all to contribute into this simple project to make better and more usable.