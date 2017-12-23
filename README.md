Killer game
===========
Django-based web application for managing killer game

### Installation
- Download this repo and setup virtual environment
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

Have fun playing! :)
