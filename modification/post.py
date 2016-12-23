import render

from google.appengine.ext import db
from helper.handler import Handler
from engineer.post import blog_key
from helper.database import Post


"""
########## Post ##########
"""


class NewPost(Handler):
    def get(self):
        if self.user:
            self.render("newpost.html")
        else:
            self.redirect("/user/login")


    def post(self):
        if not self.user:
            return self.redirect('/blog')

        subject = self.request.get('subject')
        content = self.request.get('content')

        if subject and content:
            # store post object in database
            p = Post(parent=blog_key(), user_id = self.user.key().id(),
                     subject=subject, content=content)
            p.put()
            self.redirect('/blog/%s' % str(p.key().id()))
        else:
            error = "Need to have both title and content!"
            self.render("newpost.html", subject=subject, 
                        content=content, error=error)


class EditPost(Handler):
    def get(self, post_id):
        if self.user:
            key = db.Key.from_path('Post', int(post_id), parent=blog_key())
            post = db.get(key)

            if post.user_id == self.user.key().id():
                self.render("editpost.html", subject=post.subject,
                            content=post.content, post_num=post.key().id())
            else:
                error = "You can't edit someone else's post."
                self.redirect("/blog/" + post_id + "?error=You don't have " +
                              "access to edit this record.")
        else:
            self.redirect("/user/login?error=You need to be logged, " +
                          "in order to edit your post.")


    def post(self, post_id):
        key = db.Key.from_path('Post', int(post_id), parent=blog_key())
        post = db.get(key)
        if post.user_id != self.user.key().id():
            return self.redirect('/blog')

        subject = self.request.get('subject')
        content = self.request.get('content')

        if subject and content:
            # key = db.Key.from_path('Post', int(post_id), parent=blog_key())
            # post = db.get(key)
            post.subject = subject
            post.content = content
            post.put()
            self.redirect('/blog/%s' % post_id)
        else:
            error = "Need to have both title and content!"
            self.render("editpost.html", subject=subject,
                        content=content, error=error)


class DeletePost(Handler):
    def get(self, post_id):
        if self.user:
            key = db.Key.from_path('Post', int(post_id), parent=blog_key())
            post = db.get(key)

            posts = db.GqlQuery("select * from Post order by created desc")

            if post.user_id == self.user.key().id():
                post.delete()
                self.redirect('/blog')
            else:
                self.redirect("/blog/" + post_id + "?error=You don't have " +
                              "access to delete this record.")
        else:
            self.redirect("/user/login?error=You need to be logged, in order" +
                          " to delete your post!!")
