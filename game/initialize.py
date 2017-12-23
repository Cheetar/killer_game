import os
from random import shuffle

from django.conf import settings
from django.contrib.auth.models import User

from game.models import Player


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
    player = Player()
    player.user = user
    player.generate_signatures()
    player.generate_qrcode()
    player.save()


def generate_players():
    # To every user that is not admin attach Player object
    for user in User.objects.filter(is_staff=False):
        add_player(user)
    generate_targets()


def delete_all_players():
    # Not intended to be used in real app, just for debugging purposes
    Player.objects.all().delete()
    # QR codes are stored in /media/qr_codes/
    # when deleting players, all the QR codes perish
    os.system('rm ' + settings.MEDIA_ROOT + '/qrcodes/*')


def restart_players():
    # Not intended to be used in real app, just for debugging purposes
    delete_all_players()
    generate_players()
