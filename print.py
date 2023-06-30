import sys

orig_print = print

def print(message):
    orig_print(message)
    sys.stdout.flush()