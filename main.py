"""
Udacity Fullstack Nanodegree
Multi-user blog
Author: Zee Chen
Created: 12/15/2016

== Main Module ==
1. General
2. Database
3. Render
4. Secure
5. Handler
6. User
7. Blog

"""

"""
#### General Module ####
"""

import re
import webapp2

"""
#### Database Module ####
"""

from google.appengine.ext import db
from helper.database import Post, Comment, Like

"""
#### Render Module ####
"""

import render

"""
#### Handler Module ####
"""

from helper.handler import Handler

""" 
#### User Module ####
"""

from engineer.user import SignUp, Register, Login, Logout

""" 
#### Blog Module ####
"""

from modification.comment import EditComment, DeleteComment
from modification.post import NewPost, EditPost, DeletePost
from engineer.post import BlogFront, PostPage


class Welcome(Handler):
      def get(self):
            self.render('index.html')



app = webapp2.WSGIApplication([('/', Welcome),
                               ('/blog/?', BlogFront),
                               ('/user/signup', Register),
                               ('/user/login', Login),
                               ('/user/logout', Logout),                               
                               ('/blog/newpost', NewPost),
                               ('/blog/([0-9]+)', PostPage),
                               ('/blog/deletepost/([0-9]+)', DeletePost),
                               ('/blog/editpost/([0-9]+)', EditPost),
                               ('/blog/deletecomment/([0-9]+)/([0-9]+)', DeleteComment),
                               ('/blog/editcomment/([0-9]+)/([0-9]+)', EditComment)
                               ],
                               debug=True)
