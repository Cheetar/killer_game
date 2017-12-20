from datetime import datetime, timedelta

from django.test import Client, TestCase, override_settings
from django.urls import reverse


class TimeIndex(TestCase):

    def setUp(self):
        self.client = Client()

    @override_settings(game_start=str(datetime.now() + timedelta(days=1)))
    @override_settings(game_end=str(datetime.now() + timedelta(days=2)))
    def test_index_before_game(self):
        url = reverse('game:index')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'game/index.html')
        self.assertContains(response, 'Sign up')

    @override_settings(game_start=str(datetime.now() - timedelta(days=1)))
    @override_settings(game_end=str(datetime.now() + timedelta(days=1)))
    def test_index_during_game(self):
        url = reverse('game:index')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'game/dashboard.html')
        self.assertContains(response, 'Dashboard')

    @override_settings(game_start=str(datetime.now() - timedelta(days=2)))
    @override_settings(game_end=str(datetime.now() - timedelta(days=1)))
    def test_index_after_game(self):
        url = reverse('game:index')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'game/statistics.html')
        self.assertContains(response, 'Game has ended')
