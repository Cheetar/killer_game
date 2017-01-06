import os
import socket
from random import shuffle

import qrcode
from django.contrib.auth.models import User

from game.models import Game, Player


# TODO initialize the game after game started
# TODO end the game after game end / if there are only two players alive

def generate_targets():
    players = list(Player.objects.all())
    shuffle(players)
    for i in range(len(players)):
        players[i].current_target = players[(i + 1) % len(players)]
        players[i].save()


def add_player(user):
    player = Player()
    player.user = user
    player.game = Game.objects.get(pk=1)

    player.generate_signatures()
    player.generate_qrcode()
    player.save()


def generate_players():
    # To every user attach Player object
    # TODO create Player object only for non-admin users
    for user in User.objects.all():
        add_player(user)
    generate_targets()


def delete_all_players():
    # Not intended to be used in real app, just for debugging purposes
    Player.objects.all().delete()


def restart_players():
    # Not intended to be used in real app, just for debugging purposes
    delete_all_players()
    generate_players()
