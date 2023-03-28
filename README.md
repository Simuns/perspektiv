# description
This project was a way for me to learn how webdevelopment works. It allowed me to experiment with:
* flask and jinja2 templating
* fun stuff with databases :D
* html, css and javascript
* deployment via:
    * docker build
    * pip environments

Website is just a simple website that lets you post and view letters.(skrivarabrøv) as we call them where i come from.
My goal was to write something beautiful with as little code as possible. Although this is still very much working progress.


### My plan is to include these extra features as time goes:
- [ ] styled page for each letter
- [ ] Letter verification via SMS and captcha
- [ ] scroll and load more content on frontpage
- [ ] picture compression to save some space

# installation guides
## Install via docker

* build container `docker build -t skrivarin:latest github.com/simuns/skrivarin`
* activating container `docker run --rm -p 5000:5000 skrivarin`

## Install via pipenv

* clone and enter the project 
    * `git clone https://github.com/simuns/skrivarin.git`
    * `cd skrivarin`
* install dependencies to git environment `pipenv install`
* activate environment `pipenv shell`
* Create database
    * `cd src/webapp/`
    * `flask initdb`
* run webserver `flask run`