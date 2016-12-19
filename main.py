"""
Udacity Fullstack Nanodegree
Multi-user blog
Author: Zee Chen
Created: 12/15/2016

== Main Module ==
- register form
- login form
- redirect to welcome page once logged in
- logout redirect user to register page
- edit own post
- delete own post
- like posts
- unlike posts
- check for registration errors
- incorporate cookie and cookie hashing into sign up form
- identify existent users

"""

import re
import hmac
import hashlib

import webapp2

import random
from string import letters

from google.appengine.ext import db

import os
import jinja2


"""
############################## Render Module ##############################
"""
# template directory >>> current-directory/templates
template_dir = os.path.join(os.path.dirname(__file__), 'templates')
# jinja looks for templates in template_dir
# auto escape on
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
                                        autoescape = True)


def render_str(template, **params):
    # load template file and create jinja template t
    # returns string
    t = jinja_env.get_template(template)
    return t.render(params)


"""
############################## Secure Module ##############################
"""

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


"""
############################## Handler Module ##############################
"""

"""
########## Blog Page Handler ##########
private functions (usage):
- write (write to webpage)
- render_str + render (help render webpage)
- set secure cookie (hash cookie and add to header)
- read secure cookie (check cookie validity)
- login (make user id into hashed cookie)
- logout (clear hashed cookie in header to redirect user to signup page)
- initialize (check to see if user is logged in)
"""
class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        params['user'] = self.user
        return render_str(template, **params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

    def set_secure_cookie(self, name, val):
        cookie_val = make_secure_val(val)
        self.response.headers.add_header(
            'Set-Cookie',
            '%s=%s; Path=/' % (name, cookie_val))

    def read_secure_cookie(self, name):
        cookie_val = self.request.cookies.get(name)
        return cookie_val and check_secure_val(cookie_val)

    def login(self, user):
        self.set_secure_cookie('user_id', str(user.key().id()))

    def logout(self):
        self.response.headers.add_header('Set-Cookie', 'user_id=; Path=/')

    def initialize(self, *a, **kw):
        webapp2.RequestHandler.initialize(self, *a, **kw)
        uid = self.read_secure_cookie('user_id')
        self.user = uid and User.by_id(int(uid))



""" 
############################## User Module ##############################
"""


"""
########## Save Login Info To Database ##########
- name >>> required
- password >>> required
- email >>> optional
"""
class User(db.Model):
    name = db.StringProperty(required = True)
    pw_hash = db.StringProperty(required = True)
    email = db.StringProperty()

    # get user by id function
    # @classmethod >>> decorator
    # cls refers to class User not instance of User
    # ex: User.by_id(<id>) >>> call get_by_id function (built into datastore) to load user onto database
    @classmethod
    def by_id(self, uid):
        return User.get_by_id(uid, parent = users_key())

    # get user by name function
    # uses datastore procedural code for doing database look up instead of Google SQL (GQL)
    @classmethod
    def by_name(self, name):
        u = User.all().filter('name =', name).get()
        return u

    # register function
    # takes name, password, and email and creates a new user object
    # 1. creates password hash from name and password
    # 2. creates user object
    # does not store user
    @classmethod
    def register(self, name, pw, email = None):
        pw_hash = make_pw_hash(name, pw)
        return User(parent = users_key(),
                    name = name,
                    pw_hash = pw_hash,
                    email = email)

    # login function
    @classmethod
    def login(self, name, pw):
        u = self.by_name(name)
        if u and valid_pw(name, pw, u.pw_hash):
            return u

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
            self.redirect('/')


class Login(Handler):
    def get(self):
        self.render('login-form.html')

    def post(self):
        username = self.request.get('username')
        password = self.request.get('password')

        u = User.login(username, password)
        if u:
            self.login(u)
            self.redirect('/')
        else:
            msg = 'Invalid login'
            self.render('login-form.html', error = msg)


class Logout(Handler):
    def get(self):
        self.logout()
        self.redirect('/')


""" 
############################## Blog Module ##############################
"""


def blog_key(name = 'default'):
    # blog parent key
    return db.Key.from_path('blogs', name)

"""
########## Post ##########
- render front page with latest 10 blog entries
- render new post page
- saves blog posts to database
"""
class Post(db.Model):
    # each post needs to have author, subject, content, and date created
    user_id = db.IntegerProperty(required=True)
    subject = db.StringProperty(required = True)
    content = db.TextProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)
    last_modified = db.DateTimeProperty(auto_now = True)


    def getAuthor(self):
        # get author of post
        user = User.by_id(self.user_id)
        return user.name


    def render(self):
        # render post using object data
        self._render_text = self.content.replace('\n', '<br>')
        return render_str("post.html", p = self)


class BlogFront(Handler):
    def get(self):
        # looks up all post ordered by creation time
        posts = db.GqlQuery("select * from Post order by created desc")
        self.render('front.html', posts = posts)


class PostPage(Handler):
    def get(self, post_id):
        key = db.Key.from_path('Post', int(post_id), parent=blog_key())
        post = db.get(key)

        if not post:
            self.error(404)
            return

        self.render("permalink.html", post = post)


    def post(self, post_id):
        # uid = self.read_secure_cookie('user_id')
        # find post with post_id (passed in from URL) whose parent is blog_key
        key = db.Key.from_path('Post', int(post_id), parent=blog_key())
        # get post
        post = db.get(key)


        if not post:
            self.error(404)
            return

        self.render("permalink.html", post = post)


class NewPost(Handler):
    def get(self):
        if self.user:
            self.render("newpost.html")
        else:
            self.redirect("/login")

    def post(self):
        if not self.user:
            self.redirect('/')

        subject = self.request.get('subject')
        content = self.request.get('content')

        if subject and content:
            # store post object in database
            p = Post(parent=blog_key(), user_id = self.user.key().id(),
                     subject=subject, content=content)
            p.put()
            self.redirect('/blog/%s' % str(p.key().id()))
        else:
            error = "subject and content, please!"
            self.render("newpost.html", subject=subject, 
                        content=content, error=error)


class EditPost(Handler):
    def get(self, post_id):
        if self.user:
            key = db.Key.from_path('Post', int(post_id), parent=blog_key())
            post = db.get(key)

            if post.user_id == self.user.key().id():
                self.render("editpost.html", subject=post.subject,
                            content=post.content)
            else:
                self.redirect("/blog/" + post_id + "?error=You don't have " +
                              "access to edit this record.")
        else:
            self.redirect("/login?error=You need to be logged, " +
                          "in order to edit your post.")


    def post(self, post_id):
        if not self.user:
            self.redirect('/blog')

        subject = self.request.get('subject')
        content = self.request.get('content')

        if subject and content:
            key = db.Key.from_path('Post', int(post_id), parent=blog_key())
            post = db.get(key)
            post.subject = subject
            post.content = content
            post.put()
            self.redirect('/blog/%s' % post_id)
        else:
            error = "subject and content, please!"
            self.render("editpost.html", subject=subject,
                        content=content, error=error)

app = webapp2.WSGIApplication([('/?', BlogFront),
                               ('/signup', Register),
                               ('/login', Login),
                               ('/logout', Logout),                               
                               ('/newpost', NewPost),
                               ('/blog/([0-9]+)', PostPage),
                               ('/blog/editpost/([0-9]+)', EditPost)
                               ],
                               debug=True)






