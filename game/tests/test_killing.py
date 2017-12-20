from datetime import datetime, timedelta

from django.contrib.auth.models import User
from django.test import TestCase, override_settings
from django.urls import reverse

from game.initialize import generate_players
from game.models import Player
from game.views import has_game_ended, has_game_started


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

    # check if killing works well e.g. kills counter incrises, victim is dead
    # after two kills in a row no bugs in getting the killer's player
    # game ends if there are two players alive
    # after killing a victim killer takes the current_target of victim
    # check if kill chain is a cycle
    # check if link stored in QR code kills the player (no 404, the right
    # player is killed)
    @override_settings(GAME_START=datetime.now() - timedelta(days=1))
    @override_settings(GAME_END=datetime.now() + timedelta(days=1))
    def test_kill(self):
        user1 = User.objects.get(username="user1")
        player1 = Player.objects.get(user=user1)
        player2 = player1.current_target
        user2 = player2.user
        player3 = player2.current_target
        user3 = player3.user
        player4 = player3.current_target
        user4 = player4.user
        player5 = player4.current_target
        user5 = player5.user

        self.assertEqual(player5.current_target, player1)
        self.assertEqual(has_game_started(), True)
        self.assertEqual(has_game_ended(), False)

        # player 1 kills player 2
        url = reverse('game:kill', args=[player2.kill_signature])
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'game/kill.html')
        self.assertContains(response, str(player1) + ' killed ' + str(player2))

        # player 1 kills player 3
        url = reverse('game:kill', args=[player3.kill_signature])
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'game/kill.html')
        self.assertContains(response, str(player1) + ' killed ' + str(player3))

        # player 5 kills player 1
        url = reverse('game:kill', args=[player1.kill_signature])
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'game/kill.html')
        self.assertContains(response, str(player5) + ' killed ' + str(player1))

        # Updating players status after kills
        player1 = Player.objects.get(user=user1)
        player2 = Player.objects.get(user=user2)
        player3 = Player.objects.get(user=user3)
        player4 = Player.objects.get(user=user4)
        player5 = Player.objects.get(user=user5)

        self.assertEqual(player1.kills, 2)
        self.assertEqual(player2.kills, 0)
        self.assertEqual(player3.kills, 0)
        self.assertEqual(player4.kills, 0)
        self.assertEqual(player5.kills, 1)
        self.assertEqual(player1.alive, False)
        self.assertEqual(player2.alive, False)
        self.assertEqual(player3.alive, False)
        self.assertEqual(player4.alive, True)
        self.assertEqual(player5.alive, True)
        self.assertEqual(has_game_ended(), True)
