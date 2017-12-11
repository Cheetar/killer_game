from __future__ import unicode_literals

import os
import StringIO

import qrcode
from django import forms
from django.contrib.auth.models import User
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.db import models
from django.forms import ModelForm
from django.utils.encoding import python_2_unicode_compatible

DOMAIN = "http://localhost:8000/"


class Game(models.Model):
    # TODO find a better way to deal with storing the game start and end
    """ This class stores only information about the game start and end.
        Every player is linked to a game.
    """
    name = models.CharField(max_length=200, blank=True)
    start_date = models.DateTimeField('start_date')
    end_date = models.DateTimeField('end_date')

    def __str__(self):
        return self.name


# Decorator for correct printing of polish letters
@python_2_unicode_compatible
class Player(models.Model):
    # TODO add portrait
    """ Player class is intended to store all the data about the user that
        concerns the game e.g. number of kills, target to kill
    """
    # Link player to an user and to a game
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    game = models.ForeignKey(Game, on_delete=models.CASCADE)

    kills = models.IntegerField(default=0)
    # current_target type is a Player object
    current_target = models.ForeignKey('self', blank=True, null=True)
    """ There are two distinct signatures. Normal signature allows one to browse
        it's account. Killer in order to kill his victim, need to obtain
        the second signature, kill_signature (he may obtain it via QR code or
        by inserting the signature by hand)
        Why two signatures? Beacuese a hacker can sniff urls containing normal
        signatures, so it is no more secret. The kill_signature is only
        revealed when the victim is killed.
    """
    signature = models.CharField(max_length=32)
    kill_signature = models.CharField(max_length=32)
    qrcode = models.ImageField(
        upload_to="qrcodes", blank=True, null=True)

    alive = models.BooleanField(default=True)
    death_time = models.DateTimeField(
        'death_time', blank=True, null=True)
    """ Each dead player can describe the way he was killed (these
    descriptions are intended to be funny) e.g. "I was squashed by a giant
    ladybird" or refering to the literal act of killing "I was killed by a tall
    cunning sportsman". These descriptions (aka death notes) are presented
    at the /deathnote/ and are shown to everybody.
    """
    death_note = models.TextField(blank=True, null=True)

    def __str__(self):
        """ Whenever you call str(player) his real name(e.g. Jan Kowalski) is
            shown
        """
        return self.user.first_name + " " + self.user.last_name

    def generate_signatures(self):
        """ Signatures are 16 byte random strings. These strings are stored
            in hexadeimal form, so their length is 32.
        """
        self.signature = os.urandom(16).encode("hex")
        self.kill_signature = os.urandom(16).encode("hex")

    def get_absolute_url(self):
        return DOMAIN + "kill/" + self.kill_signature + "/"

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
    """ Storage all kills in game. Using this a player can see in /profile/
        the list of all killed victims and timestamps of these kills.
    """
    killer = models.ForeignKey(
        Player, related_name='killer', null=True, blank=True)
    victim = models.ForeignKey(
        Player, related_name='victim', null=True, blank=True)
    kill_time = models.DateTimeField('kill_time', blank=True, null=True)


class UserForm(ModelForm):
    # TODO make double password check
    # TODO integrate signup with Facebook
    """ This class is used in registration (/signup/). It allows to dynamically
        generate registration form.
    """
    password = forms.CharField(widget=forms.PasswordInput)
    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True)

    class Meta:
        model = User
        exclude = ['id']
        fields = ['username', 'password', 'first_name', 'last_name']

    def save(self, commit=True):
        # Save the provided password in hashed format
        user = super(UserForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user
