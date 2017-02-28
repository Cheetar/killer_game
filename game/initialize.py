import os
import socket
from random import shuffle

import qrcode
from django.contrib.auth.models import User

from game.models import Game, Player


# TODO initialize the game after game started (probably via cron)
# TODO end the game after game end / if there are only two players alive

def generate_targets():
    """ Make list of all players in random order. Each player have to kill
        the next player on the list. This ensures that the kill chain is a
        one big cycle- at the end of the there will be only two players.
    """
    players = list(Player.objects.all())
    shuffle(players)
    for i in range(len(players)):
        players[i].current_target = players[(i + 1) % len(players)]
        players[i].save()


def add_player(user):
    # TODO make this function a Player's constructor
    player = Player()
    player.user = user
    player.game = Game.objects.get(pk=1)

    player.generate_signatures()
    player.generate_qrcode()
    player.save()


def generate_players():
    # To every user attach Player object
    for user in User.objects.filter(is_staff=False):
        add_player(user)
    generate_targets()


def delete_all_players():
    # Not intended to be used in real app, just for debugging purposes
    # TODO after deleting a player also delete its QR code png file
    # QR codes are stored in /media/qr_codes/
    Player.objects.all().delete()


def restart_players():
    # Not intended to be used in real app, just for debugging purposes
    delete_all_players()
    generate_players()
