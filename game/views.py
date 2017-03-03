# -*- coding: UTF8 -*-

from datetime import datetime
from random import shuffle

from django.contrib.auth import logout as django_logout
from django.contrib.auth import authenticate, login
from django.http import Http404, HttpResponse
from django.shortcuts import (get_object_or_404, redirect, render,
                              render_to_response)
from django.template import RequestContext
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt, csrf_protect

from game.models import Game, Kill, Player, UserForm
from initialize import add_player


def get_player(request):
    try:
        player = request.user.player
    except:
        player = False
    return player


def index(request):
    # Check if it's before, during, or after game
    game = Game.objects.get(pk=1)
    game_ended = False
    gamed_started = False
    now = timezone.now()
    if now > game.end_date:
        game_ended = True
    if now > game.start_date:
        gamed_started = True

    # Check if user is logged in
    player = False
    if not request.user.is_anonymous() and request.user.is_authenticated() and not request.user.is_staff:
        player = Player.objects.get(user=request.user)

    if game_ended:
        return redirect('game:statistics')

    if player:
        if not gamed_started:
            return render(request, 'game/countdown.html', {'player': player})
        elif not game_ended:
            return redirect('game:profile', player.signature)
        else:
            raise Http404
    else:
        if not gamed_started:
            return render(request, 'game/index.html', {'player': player})
        elif not game_ended:
            return render(request, 'game/dashboard.html', {'player': player})
        else:
            raise Http404


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


@csrf_exempt  # TODO find out how to insert csrf tag
def signup(request):
    # If game has started or you have an account, you can't create an account
    game = Game.objects.get(pk=1)
    if timezone.now() > game.start_date or request.user.is_authenticated():
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
    return render_to_response('game/signup.html', dict(userform=uf))


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
    game = Game.objects.get(pk=1)
    game_ended = False
    if timezone.now() > game.end_date:
        game_ended = True
    return render(request, 'game/profile.html',
                  {"player": player, "kills": kills, 'game_ended': game_ended})


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
    game = Game.objects.get(pk=1)
    if timezone.now() > game.end_date:
        return redirect('game:index')

    player = get_player(request)

    victim = get_object_or_404(Player, kill_signature=kill_signature)
    # If victim is already killed
    if not victim.alive:
        return render(request, 'game/already_killed.html',

                      {'dead_player': victim, 'player': player})
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

    """ Check if there are two alive players left, if yes, change game
        end datetime to now
    """
    if len(Player.objects.filter(alive=True)) <= 2:
        game = Game.objects.get(pk=1)
        game.end_date = timezone.now()
        game.save()

    return render(request, 'game/kill.html',
                  {"victim": replace_polish_chars(str(victim)), "killer": replace_polish_chars(str(killer)), 'player': player})


def manual_kill(request):
    # If game has ended or hasn't started, redirect to index
    game = Game.objects.get(pk=1)
    if timezone.now() > game.end_date or timezone.now() < game.start_date:
        return redirect('game:index')

    player = get_player(request)

    kill_signature = request.POST.get("kill_signature", False)
    if kill_signature:
        return redirect('game:kill', kill_signature)
    return render(request, 'game/manual_kill.html', {'player': player})


def statistics(request):
    player = get_player(request)

    # If game hasn't ended yet, redirect to index
    game = Game.objects.get(pk=1)
    if timezone.now() < game.end_date:
        redirect('game:index')

    return render(request, 'game/statistics.html', {'player': player})
