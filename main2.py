import re
import os
import jinja2
import hmac

import webapp2

from google.appengine.ext import db

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


# Post Model
class Post(db.Model):
    """
        This is a Post Class, which holds blog post information.
        And helps to store/retrieve User data to/from database.

        Attributes:
            user_id (int): This is user id, who wrote the blog post.
            subject (str): This is subject line of the post.
            content (text): This is content of the post.
            created (text): This is date of the post.
    """

    user_id = db.IntegerProperty(required=True)
    subject = db.StringProperty(required=True)
    content = db.TextProperty(required=True)
    created = db.DateTimeProperty(auto_now_add=True)
    last_modified = db.DateTimeProperty(auto_now=True)

    def getUserName(self):
        """
            Gets username of the person, who wrote the blog post.
        """
        user = User.by_id(self.user_id)
        return user.name

    def render(self):
        """
            Renders the post using object data.
        """
        self._render_text = self.content.replace('\n', '<br>')
        return render_str("post.html", p=self)


secret = 'secured_secured'

# Helper functions
def make_salt(length=5):
    return ''.join(random.choice(letters) for x in xrange(length))


def make_pw_hash(name, pw, salt=None):
    if not salt:
        salt = make_salt()
    h = hashlib.sha256(name + pw + salt).hexdigest()
    return '%s,%s' % (salt, h)


def valid_pw(name, password, h):
    salt = h.split(',')[0]
    return h == make_pw_hash(name, password, salt)


def users_key(group='default'):
    return db.Key.from_path('users', group)


# User Model
class User(db.Model):
    """
        This is a User Class, which holds user information.
        And helps to store/retrieve User data to/from database.

        Attributes:
            name (int): This is name of the user.
            pw_hash (str): This is hashed password of the post.
            email (text): This is email of the user.
    """
    name = db.StringProperty(required=True)
    pw_hash = db.StringProperty(required=True)
    email = db.StringProperty()

    @classmethod
    def by_id(self, uid):
        """
            This method fetchs User object from database, whose id is {uid}.
        """
        return User.get_by_id(uid, parent=users_key())

    @classmethod
    def by_name(self, name):
        """
            This method fetchs List of User objects from database,
            whose name is {name}.
        """
        u = User.all().filter('name =', name).get()
        return u

    @classmethod
    def register(self, name, pw, email=None):
        """
            This method creates a new User in database.
        """
        pw_hash = make_pw_hash(name, pw)
        return User(parent=users_key(),
                    name=name,
                    pw_hash=pw_hash,
                    email=email)

    @classmethod
    def login(self, name, pw):
        """
            This method creates a new User in database.
        """
        u = self.by_name(name)
        if u and valid_pw(name, pw, u.pw_hash):
            return u


def make_secure_val(val):
    """
        Creates secure value using secret.
    """
    return '%s|%s' % (val, hmac.new(secret, val).hexdigest())


def check_secure_val(secure_val):
    """
        Verifies secure value against secret.
    """
    val = secure_val.split('|')[0]
    if secure_val == make_secure_val(val):
        return val


class BlogHandler(webapp2.RequestHandler):
    """
        This is a BlogHandler Class, inherits webapp2.RequestHandler,
        and provides helper methods.
    """
    def write(self, *a, **kw):
        """
            This methods write output to client browser.
        """
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        """
            This methods renders html using template.
        """
        params['user'] = self.user
        return render_str(template, **params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

    def set_secure_cookie(self, name, val):
        """
            Sets secure cookie to browser.
        """
        cookie_val = make_secure_val(val)
        self.response.headers.add_header(
            'Set-Cookie',
            '%s=%s; Path=/' % (name, cookie_val))

    def read_secure_cookie(self, name):
        """
            Reads secure cookie to browser.
        """
        cookie_val = self.request.cookies.get(name)
        return cookie_val and check_secure_val(cookie_val)

    def login(self, user):
        """
            Verifies user existance.
        """
        self.set_secure_cookie('user_id', str(user.key().id()))

    def logout(self):
        """
            Removes login information from cookies.
        """
        self.response.headers.add_header('Set-Cookie', 'user_id=; Path=/')

    def initialize(self, *a, **kw):
        """
            This methods gets executed for each page and
            verfies user login status, using oookie information.
        """
        webapp2.RequestHandler.initialize(self, *a, **kw)
        uid = self.read_secure_cookie('user_id')
        self.user = uid and User.by_id(int(uid))


def blog_key(name='default'):
    return db.Key.from_path('blogs', name)


class BlogFront(BlogHandler):
    def get(self):
        """
            This renders home page with all posts, sorted by date.
        """
        deleted_post_id = self.request.get('deleted_post_id')
        posts = greetings = Post.all().order('-created')
        self.render('front.html', posts=posts, deleted_post_id=deleted_post_id)


class PostPage(BlogHandler):
    def get(self, post_id):
        """
            This renders home post page with content, comments and likes.
        """
        key = db.Key.from_path('Post', int(post_id), parent=blog_key())
        post = db.get(key)

        if not post:
            self.error(404)
            return

        error = self.request.get('error')

        self.render("permalink.html", post=post)


class NewPost(BlogHandler):
    def get(self):
        if self.user:
            self.render("newpost.html")
        else:
            self.redirect("/login")

    def post(self):
        """
            Creates new post and redirect to new post page.
        """
        if not self.user:
            self.redirect('/blog')

        subject = self.request.get('subject')
        content = self.request.get('content')

        if subject and content:
            p = Post(parent=blog_key(), user_id=self.user.key().id(),
                     subject=subject, content=content)
            p.put()
            self.redirect('/blog/%s' % str(p.key().id()))
        else:
            error = "subject and content, please!"
            self.render("newpost.html", subject=subject,
                        content=content, error=error)


USER_RE = re.compile(r"^[a-zA-Z0-9_-]{3,20}$")


def valid_username(username):
    return username and USER_RE.match(username)

PASS_RE = re.compile(r"^.{3,20}$")


def valid_password(password):
    return password and PASS_RE.match(password)

EMAIL_RE = re.compile(r'^[\S]+@[\S]+\.[\S]+$')


def valid_email(email):
    return not email or EMAIL_RE.match(email)


class Signup(BlogHandler):
    def get(self):
        self.render("signup-form.html")

    def post(self):
        """
            Sign up validation.
        """
        have_error = False
        self.username = self.request.get('username')
        self.password = self.request.get('password')
        self.verify = self.request.get('verify')
        self.email = self.request.get('email')

        params = dict(username=self.username,
                      email=self.email)

        if not valid_username(self.username):
            params['error_username'] = "That's not a valid username."
            have_error = True

        if not valid_password(self.password):
            params['error_password'] = "That wasn't a valid password."
            have_error = True
        elif self.password != self.verify:
            params['error_verify'] = "Your passwords didn't match."
            have_error = True

        if not valid_email(self.email):
            params['error_email'] = "That's not a valid email."
            have_error = True

        if have_error:
            self.render('signup-form.html', **params)
        else:
            self.done()

    def done(self, *a, **kw):
        raise NotImplementedError


class Register(Signup):
    def done(self):
        # Make sure the user doesn't already exist
        u = User.by_name(self.username)
        if u:
            msg = 'That user already exists.'
            self.render('signup-form.html', error_username=msg)
        else:
            u = User.register(self.username, self.password, self.email)
            u.put()

            self.login(u)
            self.redirect('/')


class Login(BlogHandler):
    def get(self):
        self.render('login-form.html', error=self.request.get('error'))

    def post(self):
        """
            Login validation.
        """
        username = self.request.get('username')
        password = self.request.get('password')

        u = User.login(username, password)
        if u:
            self.login(u)
            self.redirect('/')
        else:
            msg = 'Invalid login'
            self.render('login-form.html', error=msg)


class Logout(BlogHandler):
    def get(self):
        self.logout()
        self.redirect('/')


app = webapp2.WSGIApplication([
                               ('/?', BlogFront),
                               ('/blog/([0-9]+)', PostPage),
                               ('/blog/newpost', NewPost),
                               ('/signup', Register),
                               ('/login', Login),
                               ('/logout', Logout),
                               ],
                              debug=True)
