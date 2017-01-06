Killer game
===========
Django-based web application to manage killer game

### How to run the app:
- setup postgresql database 'killer_db' with role 'killer_user' and password 'password' (may be changed in settings.py)
- `python manage.py makemigrations && python manage.py migrate` - apply migrations to DB
- `python manage.py createsuperuser` - create admin user to have access to admin panel ( at /admin/)
- install all libraries from requirements.txt (favourably via pip)
- `python manage.py runserver` - run application

### Start a game
- let all the users signup
- create players:
``` python
python manage.py shell
>>> from game.initialize import *
>>> generate_players()
```
if a game have been already running and you want to restart it (make all players alive, reset their kill counters, generate new QR codes), instead of `generate_players()` type `restart_players()`



