from __future__ import unicode_literals

import datetime
import os
import StringIO

import qrcode
from django import forms
from django.contrib.auth.models import User
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.core.urlresolvers import reverse
from django.db import models
from django.forms import ModelForm
from django.utils import timezone
from django.utils.encoding import python_2_unicode_compatible


class Game(models.Model):
    name = models.CharField(max_length=200, blank=True)
    start_date = models.DateTimeField('start_date')
    end_date = models.DateTimeField('end_date')

    def __str__(self):
        return self.name


# Decorator for correct printing of polish letters
@python_2_unicode_compatible
class Player(models.Model):
    """ Player class is intended to store all the data about the user that
        concerns the game e.g. number of kills, target to kill
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    game = models.ForeignKey(Game, on_delete=models.CASCADE)

    kills = models.IntegerField(default=0)
    # current_target type is a Player object
    current_target = models.ForeignKey('self', blank=True, null=True)
    """ There are two distinct signatures. Normal signature allows one to browse
        it's account. Killer in order to kill his victim, need to obtain
        the second signature, kill_signature (he may obtain it via QR code or
        by inserting the signature by hand)
        Why two signatures? Beacuese a hacker can sniff urls with normal
        signatures so it is no more secret. The kill_signature is only
        revealed when the victim is killed.
    """
    signature = models.CharField(max_length=32)
    kill_signature = models.CharField(max_length=32)
    qrcode = models.ImageField(
        upload_to="qrcodes", blank=True, null=True)

    alive = models.BooleanField(default=True)
    death_time = models.DateTimeField(
        'death_time', blank=True, null=True)
    """ Each killed player can describe the way he was killed (these
    descriptions are intended to be funny) e.g. "I was squashed by a giant
    ladybird" or refering to the literal act of killing "I was killed by a tall
    cunning sportsman"
    """
    death_note = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.user.first_name + " " + self.user.last_name

    def generate_signatures(self):
        self.signature = os.urandom(16).encode("hex")
        self.kill_signature = os.urandom(16).encode("hex")

    def get_absolute_url(self):
        # TODO get the domain name instead of hardcoded localhost
        return "http://127.0.0.1:8000/kill/" + self.kill_signature + "/"

    def generate_qrcode(self):
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=6,
            border=0,
        )
        qr.add_data(self.get_absolute_url())
        qr.make(fit=True)

        img = qr.make_image()

        buffer = StringIO.StringIO()
        img.save(buffer)
        filename = '%s.png' % (self.signature)
        filebuffer = InMemoryUploadedFile(
            buffer, None, filename, 'image/png', buffer.len, None)
        self.qrcode.save(filename, filebuffer)


class Kill(models.Model):
    # TODO implement Kill model
    """ Storage all kills in game. Using this a player can see in /profile/ can
        the list of all killed victims and times of kills.
    """
    pass


class UserForm(ModelForm):

    class Meta:
        password = forms.CharField(widget=forms.PasswordInput)
        widgets = {
            'password': forms.PasswordInput(),
        }
        model = User
        exclude = ['id']
        fields = ['username', 'password', 'first_name', 'last_name']