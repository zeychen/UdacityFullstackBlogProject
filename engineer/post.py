import render

from google.appengine.ext import db
from helper.handler import Handler
from helper.database import Like, Comment, Post


"""
########## Post ##########
"""
def blog_key(name = 'default'):
    # blog parent key
    return db.Key.from_path('blogs', name)
    

class BlogFront(Handler):
    def get(self):
        if (self.user):
            # looks up all post ordered by creation time
            posts = db.GqlQuery("select * from Post order by created desc")

            self.render('front.html', posts = posts)
        else:
            self.render("/user/login")


class PostPage(Handler):
    def get(self, post_id):
        key = db.Key.from_path('Post', int(post_id), parent=blog_key())
        post = db.get(key)

        comments = db.GqlQuery("select * from Comment where post_id = " +
                               post_id + " order by created desc")

        likes = db.GqlQuery("select * from Like where post_id="+post_id)

        if not post:
            self.error(404)
            return

        self.render("permalink.html", post = post, comments=comments,
                    likescount=likes.count())


    def post(self, post_id):
        # find post with post_id (passed in from URL) whose parent is blog_key
        key = db.Key.from_path('Post', int(post_id), parent=blog_key())
        # get post
        post = db.get(key)


        if not post:
            self.error(404)
            return

        if (self.user):
            if(self.request.get('like') and 
               self.request.get('like') == "update"):
                likes = db.GqlQuery("select * from Like where post_id = " +
                               post_id + "and user_id=" + str(self.user.key().id()))

                # make sure user don't like own post
                if self.user.key().id() == post.user_id:
                    self.redirect("/blog/" + post_id +
                                  "?error=You cannot like your " +
                                  "post.!!")
                elif likes.count() ==0:
                    l = Like(parent=blog_key(), user_id = self.user.key().id(),
                            post_id=int(post_id))
                    # save like entity
                    l.put()

            if(self.request.get('comment')):
                # if comment button is clicked, 
                # then create new comment entity 
                # linked to user and post data
                comm = Comment(parent=blog_key(), user_id = self.user.key().id(),
                            post_id=int(post_id), comment=self.request.get('comment'))
                # save comment entity
                comm.put()

        else:
            self.redirect("/user/login?error=You need to login, " +
                          "in order to post a comment.")

        comments = db.GqlQuery("select * from Comment where post_id = " +
                               post_id + "order by created desc")

        likes = db.GqlQuery("select * from Like where post_id="+post_id)

        self.render("permalink.html", post = post, likescount=likes.count(),
                    comments=comments )
