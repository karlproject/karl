from random import choice
import string

def friendly_random_id(size=6):
    len = int(size/2)
    return ''.join(
        [choice('bcdfghklmnprstvw')+choice('aeiou') for i in range(len)]
        )

def unfriendly_random_id(size=10):
    return ''.join(
        [choice(string.uppercase+string.digits) for i in range(size)])
