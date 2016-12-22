import render
import re
import secure

from google.appengine.ext import db
from helper.handler import Handler
from helper.database import User


"""
########## Sign Up ##########
- render sign up page
- validate user input
"""
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
        self.render("signup-form.html")

    def post(self):
        # get values from html
        have_error = False
        self.username = self.request.get('username')
        self.input_password = self.request.get('password')
        self.verify = self.request.get('verify')
        self.email = self.request.get('email')

        # store values that will be sent back to form if invalid
        params = dict(username = self.username,
                      email = self.email)

        # test values
        if not valid_username(self.username):
            params['error_username'] = "That's not a valid username."
            have_error = True

        if not valid_password(self.input_password):
            params['error_password'] = "That wasn't a valid password."
            have_error = True

        elif self.input_password != self.verify:
            params['error_verify'] = "Your passwords didn't match."
            have_error = True

        if not valid_email(self.email):
            params['error_email'] = "That's not a valid email."
            have_error = True

        # if error >>> send user back to signup form
        # if no error >>> send user to welcome page
        if have_error:
            self.render('signup-form.html', **params)
        else:
            # self.done() don't do anything but throws error message
            self.done()

    def done(self, *a, **kw):
        raise NotImplementedError


class Register(SignUp):
    def done(self):
        u = User.by_name(self.username)
        if u:
            msg = 'That user already exists.'
            self.render('signup-form.html', error_username = msg)
        else:
            u = User.register(self.username, self.input_password, self.email)
            # stores user in database
            u.put()

            # call login function to set cookie for user
            self.login(u)
            self.redirect('/blog')


class Login(Handler):
    def get(self):
        self.render('login-form.html')


    def post(self):
        username = self.request.get('username')
        password = self.request.get('password')

        u = User.login(username, password)
        if u:
            self.login(u)
            self.redirect('/blog')
        else:
            msg = 'Invalid login'
            self.render('login-form.html', error = msg)


class Logout(Handler):
    def get(self):
        self.logout()
        self.redirect('/')
