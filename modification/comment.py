import render

from google.appengine.ext import db
from helper.handler import Handler
from engineer.post import blog_key

"""
########## Comment ##########
- save comments as entities with post_id and user_id as key
"""


class EditComment(Handler):
    def get(self, post_id, comment_id):
        if self.user:
            key = db.Key.from_path('Comment', int(comment_id), parent=blog_key())
            post_key = db.Key.from_path('Post', int(post_id), parent=blog_key())
            comm = db.get(key)
            post = db.get(post_key)

            if comm.user_id == self.user.key().id():
                self.render("editcomment.html", comment=comm.comment,
                            post_num=post.key().id())
            else:
                self.redirect("/blog/" + post_id + "?error=You don't have " +
                              "access to edit this comment.")
        else:
            self.redirect("/user/login?error=You need to be logged, " +
                          "in order to edit your comment.")


    def post(self, post_id, comment_id):
        key = db.Key.from_path('Comment', int(comment_id), parent=blog_key())
        comm = db.get(key)
        if comm.user_id != self.user.key().id():
            return self.redirect('/blog')

        comment = self.request.get('comment')

        if comment:
            comm.comment = comment
            comm.put()
            self.redirect('/blog/%s' % post_id )
        else:
            error = "Need to have content, please!"
            self.render("editcomment.html", comment=comment, error=error)


class DeleteComment(Handler):
    def get(self, post_id, comment_id):
        if self.user:
            key = db.Key.from_path('Comment', int(comment_id), parent=blog_key())
            comment = db.get(key)

            comments = db.GqlQuery("select * from Comment order by created desc")

            if comment.user_id == self.user.key().id():
                comment.delete()
                self.redirect('/blog/' + post_id)
            else:
                self.redirect("/blog/" + post_id + "?error=You don't have " +
                              "access to delete this comment.")
        else:
            self.redirect("/user/login?error=You need to be logged, in order" +
                          " to delete your comment!!")
