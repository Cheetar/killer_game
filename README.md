Killer game
===========
Django-based web application for managing killer game

### What's killer game?
Have you ever wanted taste a life of a serial killer? With this game you can become one and set deadly traps for your prey. At the beginning you are assinged a target that you must kill. If you kill your target, his target becomes yours. All the players are assigned in a cycle, so in the end there are 2 people left. You can kill your target only if you are both alone and there are no witnesses of this incident. Killing can be done by simply touching your target's arm and saying "I kill you".

This game is desiged to be played by a lot of people, so there is absolutely no problem to play with 100+ people. It suits perfectly all sorts of camps where you want to integrate people.

### Installation
- Download this repo `git clone https://github.com/Cheetar/killer_game.git` and setup virtual environment (http://docs.python-guide.org/en/latest/dev/virtualenvs/)
- Install dependencies `pip install -r requirements.txt`
- Create an .env file with custom settings suiting your needs (you can update .env.example accordingly and save it as .env)
- Migrate data to database `python manage.py migrate`
- Create admin account `python manage.py createsuperuser`
- Start the app `python manage.py runserver`

### Usefull info
- Game starts automatically after *game_start* defined in .env
- After game has started users cannot sign up
- If you don't want to use SSL add `SECURE_SSL_REDIRECT=False` to .env  as well as `SESSION_COOKIE_SECURE=False`
- When game is initialized a file called *.initialized* is created. If you want to restart the game (i.e. make all players alive, generate a new random kill cycle) simply remove the *.initialized* file
- Killing can be done by scanning a QR code. Alternatively you can rewrite the secret code by hand

### Tests
- To run tests: `python manage.py test`

### Screenshots

![Sign up](https://raw.githubusercontent.com/Cheetar/killer_game/master/scr_signup.png)
![QR codes](https://raw.githubusercontent.com/Cheetar/killer_game/master/scr_qrcode.png)

Have fun playing! :)
