from google.appengine.ext import db
import render
import secure

"""
########## Save User Info To Database ##########
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
        return User.get_by_id(uid, parent = secure.users_key())

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
        pw_hash = secure.make_pw_hash(name, pw)
        return User(parent = secure.users_key(),
                    name = name,
                    pw_hash = pw_hash,
                    email = email)

    # login function
    @classmethod
    def login(self, name, pw):
        u = self.by_name(name)
        if u and secure.valid_pw(name, pw, u.pw_hash):
            return u


"""
########## Save Post Info To Database ##########
- author >>> required
- subject >>> required
- content >>> required
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
        return render.helper_render_str("post.html", p = self)


"""
########## Save Comments To Database ##########
- user >>> required
- post >>> required
- comment >>> required
"""


class Comment(db.Model):
    # each post needs to have author, subject, content, and date created
    user_id = db.IntegerProperty(required=True)
    post_id = db.IntegerProperty(required=True)
    comment = db.TextProperty(required=True)
    created = db.DateTimeProperty(auto_now_add=True)
    last_modified = db.DateTimeProperty(auto_now=True)

    def getAuthor(self):
        user = User.by_id(self.user_id)
        return user.name


"""
########## Save Comments To Database ##########
- user >>> required
- post >>> required
"""


class Like(db.Model):

    user_id = db.IntegerProperty(required=True)
    post_id = db.IntegerProperty(required=True)


    def getAuthor(self):
        user = User.by_id(self.user_id)
        return user.name
