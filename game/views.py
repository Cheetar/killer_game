from random import shuffle

from django.contrib.auth import logout as django_logout
from django.contrib.auth import authenticate, login
from django.http import HttpResponse
from django.shortcuts import (get_object_or_404, redirect, render,
                              render_to_response)
from django.template import RequestContext
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt, csrf_protect

from game.models import Game, Kill, Player, UserForm
from initialize import add_player


def index(request):
    # TODO FRONTEND, countdown if game haven't started yet
    # hasn't started yet

    # If you are logged in you are redirected to profile
    player = False
    if not request.user.is_anonymous() and request.user.is_authenticated() and not request.user.is_staff:
        player = Player.objects.get(user=request.user)
        return redirect('game:profile', player.signature)
    return render(request, 'game/index.html',
                  {'player': player})


def login_user(request):
    # You can't login if you are already logged in
    if request.user.is_authenticated():
        return redirect('game:index')

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
    if request.user.is_authenticated():
        return redirect('game:index')

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
                          {"username": user.username, 'player': user.player}
                          )
    else:
        uf = UserForm(prefix='user')
    return render_to_response('game/signup.html', dict(userform=uf))


def rules(request):
    try:
        player = request.user.player
    except:
        player = False
    return render(request, 'game/rules.html', {'player': player})


def living(request):
    try:
        player = request.user.player
    except:
        player = False

    # Get all alive players
    living = list(Player.objects.filter(alive=True))
    # Sort alphabetically players to avoid leaking kill chain information
    living = sorted(living, key=str)
    # Sort them by number of kills
    living = sorted(living, key=lambda player: -player.kills)
    return render(request, 'game/living.html',
                  {'living': living, 'player': player})


def deathnote(request):
    try:
        player = request.user.player
    except:
        player = False

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
                  {"player": player, "kills": kills})


def profile_qr(request, signature):
    player = get_object_or_404(Player, signature=signature)
    return render(request, 'game/profile_qr.html', {"player": player})


def kill(request, kill_signature):
    """ User can acces this view only by scanning QR code of the victim or by
        manually inserting killing signature
    """
    try:
        player = request.user.player
    except:
        player = False

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

    return render(request, 'game/kill.html',
                  {"victim": victim, "killer": killer})


def manual_kill(request):
    try:
        player = request.user.player
    except:
        player = False

    kill_signature = request.POST.get("kill_signature", False)
    if kill_signature:
        return redirect('game:kill', kill_signature)
    return render(request, 'game/manual_kill.html', {'player': player})
