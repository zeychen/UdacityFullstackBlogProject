
import re
import hmac
import hashlib

import random
from string import letters

from google.appengine.ext import db

"""
########## Hash User Cookie ##########
- hash cookies to prevent user fraud
"""

SECRET = "Sl33pyZ0ey"

def make_secure_val(value):
    return "%s|%s" % (value, hmac.new(SECRET,value).hexdigest())

def check_secure_val(secure_val):
    val = secure_val.split('|')[0]
    if secure_val == make_secure_val(val):
        return val   


"""
########## Hash Password ##########
- password security
"""
def make_salt(length = 5):
    return ''.join(random.choice(letters) for x in xrange(length))

def make_pw_hash(name, pw, salt = None):
    if not salt:
        salt = make_salt()
    h = hashlib.sha256(name + pw + salt).hexdigest()
    return '%s,%s' % (salt, h)

def valid_pw(name, password, h):
    salt = h.split(',')[0]
    return h == make_pw_hash(name, password, salt)

# store user
def users_key(group = 'default'):
    return db.Key.from_path('users', group)
