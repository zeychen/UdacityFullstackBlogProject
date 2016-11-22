import os
import re
import hashlib
import webapp2
import jinja2

from google.appengine.ext import db
"""
Udacity Fullstack Nanodegree
User Account and Security
Registration Quiz

- create sign up form
- check for registration errors
- redircts user to welcome page if sign up successful
- incorporate cookie and cookie hashing into sign up form
- identify existent users
"""

########## hash cookie ##########
SECRET = "Sl33pyZ0ey"

def hash_str(s):
    # Hash cookies using sha256
    # return hashlib.md5(s).hexdigest()
    # Hash cookies using hmac
    return hashlib.sha256(SECRET+s).hexdigest()

# prevent forge
def make_secure_val(s):
    return "%s|%s" % (s, hash_str(s))

def check_secure_val(h):
    s = h.split('|')[0]
    if h == make_secure_val(s):
        return s
    else:
        return None

########## hash password ##########
def make_salt():
    return ''.join(random.choice(string.letters) for x in xrange(5))

def make_pw_hash(name, pw, salt = None):
    if not salt:
        salt = make_salt()
    h = hashlib.sha256(name + pw + salt).hexdigest()
    return '%s,%s' % (h, salt)
    
def valid_pw(name, pw, h):
    salt = h.split(',')[1]
    if h == make_pw_hash(name, pw, salt):
        return True

########## jinja template for rendering ##########
# template directory >>> current-directory/templates
template_dir = os.path.join(os.path.dirname(__file__), 'templates')
# jinja looks for templates in template_dir
# auto escape on
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
										autoescape = True)

# load template file and create jinja template t
# returns string

def render_str(template, **params):
    t = jinja_env.get_template(template)
    return t.render(params)

class Handler(webapp2.RequestHandler):
    def render(self, template, **kw):
        self.response.out.write(render_str(template, **kw))

    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)


########## Sign Up ##########
# match requirements
USER_RE = re.compile(r"^[a-zA-Z0-9_-]{3,20}$")
def valid_username(username):
    return username and USER_RE.match(username)

PASS_RE = re.compile(r"^.{3,20}$")
def valid_password(password):
    return password and PASS_RE.match(password)

# optional email >>> either no email or match requirement
EMAIL_RE  = re.compile(r'^[\S]+@[\S]+\.[\S]+$')
def valid_email(email):
    return not email or EMAIL_RE.match(email)

class SignUp(Handler):

    def get(self):
        #render sign up form
        self.render("user.html")
        # cookie object
        # cookie.get >>> check in dictionary to see if key exists
            # if key doesn't exist then set to default value of 0
        visits = 0
        visits_cookie_str = self.request.cookies.get('visits')
        # if cookie exists then convert cookie to integer
        if visits_cookie_str:
            cookie_val = check_secure_val(visits_cookie_str)
            if cookie_val:
                visits = int(cookie_val)
        visits += 1

        # call make secure function
        new_cookie_val = make_secure_val(str(visits))

        # set cookie
        self.response.headers.add_header('Set-Cookie', 'visits=%s' % new_cookie_val)

        # special message
        # if visits > 10:
        #     self.write("You are the best ever")
        # else:
        #     self.write("You've been to the site %s times" % visits)

    def post(self):
        # get values from html
        have_error = False
        username = self.request.get('username')
        password = self.request.get('password')
        verify = self.request.get('verify')
        email = self.request.get('email')

        # store values that will be sent back to form if invalid
        params = dict(username = username,
                      email = email)

        # test values
        if not valid_username(username):
            params['error_username'] = "That's not a valid username."
            have_error = True

        if not valid_password(password):
            params['error_password'] = "That wasn't a valid password."
            have_error = True
        elif password != verify:
            params['error_verify'] = "Your passwords didn't match."
            have_error = True

        if not valid_email(email):
            params['error_email'] = "That's not a valid email."
            have_error = True

        # if error >>> send user back to signup form
        # if no error >>> send user to welcome page
        if have_error:
            self.render('user.html', **params)
        else:
            self.redirect('/welcome?username=' + username)

########## Welcome ##########
class Welcome(Handler):
    def get(self):
        username = self.request.get('username')
        if valid_username(username):
            self.render('welcome.html', username = username)
        else:
            self.redirect('/signup')


app = webapp2.WSGIApplication([('/signup', SignUp),
                               ('/welcome', Welcome)],
                              debug=True)






