from django.contrib.auth.models import User
from django.test import TestCase

from game.initialize import generate_players
from game.models import Player


class KillingTest(TestCase):
    no_players = 5

    def setUp(self):
        for i in range(1, self.no_players + 1):
            User.objects.create_user(username='user' + str(i), email='foo@bar.com', password='qwertyqwerty')
        generate_players()

    def test_is_kill_chain_cycle(self):
        user1 = User.objects.get(username="user1")
        player1 = Player.objects.get(user=user1)
        curr_player = player1.current_target
        for i in range(self.no_players - 1):
            self.assertNotEqual(curr_player, player1)
            curr_player = curr_player.current_target
        self.assertEqual(curr_player, player1)

# TODO tests
# check if killing works well e.g. kills counter incrises, victim is dead
# after two kills in a row no bugs in getting the killer's player
# object(two players with the same current_target)
# game ends if there are two players alive
# after killing a victim killer takes the current_target of victim
# DONE check if kill chain is a cycle
# check if link stored in QR code kills the player (no 404, the right
# player is killed)
