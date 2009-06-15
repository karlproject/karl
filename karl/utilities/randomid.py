from random import choice

def friendly_random_id(size=6):
    len = int(size/2)
    return ''.join(
        [choice('bcdfghklmnprstvw')+choice('aeiou') for i in range(len)]
        )

