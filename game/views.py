# -*- coding: UTF8 -*-

import datetime
import time
from os import path, system

from django.conf import settings
from django.contrib.auth import logout as django_logout
from django.contrib.auth import authenticate, login
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import get_object_or_404, redirect, render
from django.urls.exceptions import NoReverseMatch
from django.utils import timezone

from game.models import Kill, Player, UserForm
from initialize import add_player, restart_players


def get_player(request):
    # Create player profiles if game has started and it hadn't been done yet
    if (not path.isfile(settings.MEDIA_ROOT + "/.initialized") and has_game_started()):
        restart_players()
        system("touch " + settings.MEDIA_ROOT + "/.initialized")
        time.sleep(2)

    player = False
    if not request.user.is_anonymous() and request.user.is_authenticated() and not request.user.is_staff:
        try:
            player = Player.objects.get(user=request.user)
        except ObjectDoesNotExist:
            pass
    return player


def get_game_start():
    return settings.GAME_START


def get_game_end():
    return settings.GAME_END


def datetime_to_timestamp(dt):
    return time.mktime(dt.timetuple())


def has_game_started():
    now = datetime.datetime.now()
    game_start = get_game_start()
    return now > game_start


def has_game_ended():
    now = datetime.datetime.now()
    game_end = get_game_end()
    no_alive_player = len(Player.objects.filter(alive=True))
    return (has_game_started() and no_alive_player <= 2) or now > game_end


def get_best_killer():
    # Returns the player that have most kills and is alphabetically first
    return Player.objects.all().exclude(kills=0).order_by('str').order_by('alive').order_by('-kills').first()


def get_last_deathnote():
    note = None
    player = Player.objects.filter(alive=False).exclude(death_note=None).order_by('death_time').first()
    if player:
        note = player.death_note
    return note


def get_survivors():
    return Player.objects.filter(alive=True)


def get_last_kill():
    kills = Kill.objects.order_by('kill_time')
    return kills.first()


def index(request):
    game_start = get_game_start()
    game_started = has_game_started()
    game_ended = has_game_ended()
    player = get_player(request)

    if game_ended:
        return redirect('game:statistics')

    if request.user.is_authenticated():
        if not game_started:
            timestamp = datetime_to_timestamp(game_start)
            return render(request, 'game/countdown.html', {'player': player, 'game_start_date': timestamp})
        elif player:
            return redirect('game:profile', player.signature)
        else:
            return render(request, 'game/dashboard.html', {'best_killer': get_best_killer(),
                                                           'last_note': get_last_deathnote(),
                                                           'last_kill': get_last_kill()})
    else:
        if not game_started:
            return render(request, 'game/index.html', {'player': player})
        else:
            return render(request, 'game/dashboard.html', {'best_killer': get_best_killer(),
                                                           'last_note': get_last_deathnote(),
                                                           'last_kill': get_last_kill()})


def login_user(request):
    # You can't login if you are already logged in
    if request.user.is_authenticated():
        return redirect('game:index')

    # Manage logging in
    username = request.POST.get('username', False)
    password = request.POST.get('password', False)
    # If user hadn't attempted to login don't show that credentials are invalid
    if not username and not password:
        return render(request, 'game/login.html',
                      {'failed_attempt': 'False', })
    # Try to log in user
    user = authenticate(username=username, password=password)
    if user is not None:
        # Successfully authenticated
        login(request, user)
        return redirect('game:index')
    else:
        # Show that username/password is invalid
        return render(request, 'game/login.html', {'failed_attempt': 'True', })


def logout(request):
    # Logout, don't show anything, just redirect to index page
    django_logout(request)
    return redirect('game:index')


def signup(request):
    # If game has started or you have an account, you can't create an account
    game_started = has_game_started()
    if game_started or request.user.is_authenticated():
        return redirect('game:index')

    # Manage signup process
    if request.method == 'POST':
        uf = UserForm(request.POST, prefix='user')
        if uf.is_valid():
            # Create User object
            user = uf.save()
            # Create Player object for the user
            add_player(user)
            # Log the user in
            user = authenticate(
                username=uf.cleaned_data['username'],
                password=uf.cleaned_data['password'])
            login(request, user)
            return render(request,
                          'game/successful_signup.html',
                          {"username": user.username, 'player': user.player})
    else:
        uf = UserForm(prefix='user')
    return render(request, 'game/signup.html', dict(userform=uf))


def rules(request):
    player = get_player(request)
    return render(request, 'game/rules.html', {'player': player})


def living(request):
    player = get_player(request)

    # Get all alive players
    living = list(Player.objects.filter(alive=True))
    # Sort alphabetically players to avoid leaking kill chain information
    living = sorted(living, key=str)
    # Sort them by number of kills
    living = sorted(living, key=lambda player: -player.kills)
    return render(request, 'game/living.html',
                  {'living': living, 'player': player})


def deathnote(request):
    player = get_player(request)

    # Add a note
    note = request.POST.get("note", False)
    if note:
        player.death_note = note
        player.save()

    # Get all dead players that have written something in deathnote
    dead_players = Player.objects.filter(alive=False).exclude(death_note=None)
    return render(request, 'game/deathnote.html',
                  {'dead_players': dead_players, 'player': player})


def profile(request, signature):
    # If invalid signature show 404
    player = get_object_or_404(Player, signature=signature)
    kills = Kill.objects.filter(killer=player)
    return render(request, 'game/profile.html',
                  {"player": player, "kills": kills, 'game_ended': has_game_ended()})


def profile_qr(request, signature):
    player = get_object_or_404(Player, signature=signature)
    return render(request, 'game/profile_qr.html', {"player": player})


def kill(request, kill_signature):
    def replace_polish_chars(s):
        s = s.replace('ę', 'e').replace('ó', 'o').replace('ą', 'a').replace('ś', 's').replace(
            'ł', 'l').replace('ż', 'z').replace('ź', 'z').replace('ć', 'c').replace('ń', 'n')
        return s
    """ User can acces this view only by scanning QR code of the victim or by
        manually inserting killing signature
    """
    if has_game_ended():
        return redirect('game:index')

    player = get_player(request)

    victim = get_object_or_404(Player, kill_signature=kill_signature)
    # If victim is already killed
    if not victim.alive:
        return render(request, 'game/already_killed.html', {'dead_player': victim, 'player': player})
    killer = Player.objects.get(current_target=victim)

    # Update killer's status
    killer.kills += 1
    killer.current_target = victim.current_target
    killer.save()

    # Update victim's status
    victim.alive = False
    victim.death_time = timezone.now()
    victim.current_target = None
    victim.save()

    # Add kill objects
    kill = Kill(killer=killer, victim=victim, kill_time=timezone.now())
    kill.save()

    return render(request, 'game/kill.html', {
        "victim": replace_polish_chars(str(victim)),
        "killer": replace_polish_chars(str(killer)),
        "player": player})


def manual_kill(request):
    # If game has ended or hasn't started, redirect to index
    if has_game_ended() or not has_game_started():
        return redirect('game:index')

    player = get_player(request)

    kill_signature = request.POST.get("kill_signature", False)
    if kill_signature:
        try:
            return redirect('game:kill', kill_signature)
        except NoReverseMatch:
            return render(request, 'game/invalid_kill_signature.html')
    return render(request, 'game/manual_kill.html', {'player': player})


def statistics(request):
    player = get_player(request)

    if not has_game_ended():
        return redirect('game:index')

    return render(request, 'game/statistics.html', {'player': player,
                                                    'best_killer': get_best_killer(),
                                                    'survivors': get_survivors()})
