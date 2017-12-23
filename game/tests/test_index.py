from datetime import datetime, timedelta

from django.contrib.auth.models import User
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from game.initialize import generate_players
from game.views import has_game_ended, has_game_started


class TimeIndex(TestCase):

    no_players = 5

    def setUp(self):
        self.client = Client()
        for i in range(1, self.no_players + 1):
            User.objects.create_user(username='user' + str(i), email='foo@bar.com', password='qwertyqwerty')
        generate_players()

    @override_settings(GAME_START=datetime.now() + timedelta(days=1))
    @override_settings(GAME_END=datetime.now() + timedelta(days=2))
    def test_index_before_game(self):
        self.assertEqual(False, has_game_started())
        self.assertEqual(False, has_game_ended())
        url = reverse('game:index')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'game/index.html')
        self.assertContains(response, 'Sign up')

    @override_settings(GAME_START=datetime.now() - timedelta(days=10))
    @override_settings(GAME_END=datetime.now() + timedelta(days=10))
    def test_index_during_game(self):
        self.assertEqual(True, has_game_started())
        self.assertEqual(False, has_game_ended())
        url = reverse('game:index')
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'game/dashboard.html')
        self.assertContains(response, 'Dashboard')

    @override_settings(GAME_START=datetime.now() - timedelta(days=2))
    @override_settings(GAME_END=datetime.now() - timedelta(days=1))
    def test_index_after_game(self):
        self.assertEqual(True, has_game_started())
        self.assertEqual(True, has_game_ended())
        url = reverse('game:index')
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'game/statistics.html')
        self.assertContains(response, 'Game finished')
