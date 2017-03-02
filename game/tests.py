from django.test import TestCase

# TODO tests
# check if killing works well e.g. kills counter incrises, victim is dead
# after two kills in a row no bugs in getting the killer's player
# object(two players with the same current_target)
# game ends if there are two players alive
# after killing a victim killer takes the current_target of victim
# check if kill chain is a cycle
# check if link stored in QR code kills the player (no 404, the right
# player is killed)
