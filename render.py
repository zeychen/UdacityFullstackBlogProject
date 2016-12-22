import os
import jinja2

"""
Udacity Fullstack Nanodegree
Multi-user blog
Author: Zee Chen
Created: 12/15/2016

== Render Module ==

"""


"""
########## Jinja template for rendering ##########
"""
# template directory >>> current-directory/templates
template_dir = os.path.join(os.path.dirname(__file__), 'templates')
# jinja looks for templates in template_dir
# auto escape on
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
                                        autoescape = True)


def helper_render_str(template, **params):
    # load template file and create jinja template t
    # returns string
    t = jinja_env.get_template(template)
    return t.render(params)
