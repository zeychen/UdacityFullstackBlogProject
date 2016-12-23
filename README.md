<h1>Full Circle Multi-User Blog Project</h1>

This project is part of Udacity Fullstack Nanodegree program. The goal here is to create a simple multi-user blog with login/logout, create/edit/delete posts, and comments within restrictions, and like posts.

Checkout the <a href="https://full-circle-153317.appspot.com">live</a> version of this project.

<h3>Project specifications</h3>
1. Front page - prompts user to login or signup.
2. Main page - lists all blog posts according to date creation.
3. Post page - blog posts have individual pages along with ability to edit, delete, comment, or like. 
4. Comment page - comments show up in blog post pages with ability to edit or delete own comments on comment page.
5. Login/signup page - validates user input and displays error(s) when necessary.

User is redirected to login page if trying to access page without being signed in.
User can only edit or delete own posts and comments.
User can't like own post.

Code conforms to the Python Style Guide (PEP8)

<h3>Running the project</h3>
1. Install Python if necessary.
2. Sign up for a free Google App Engine account.
3. Install Google App Engine SDK.
5. Navigate to project root folder.
6. Initiate Google App Engine with 'gcloud init'.
7. Choose default settings.
8. Type 'dev_appserver.py .' in project root folder.
9. Visit localhost:8080 in browser.