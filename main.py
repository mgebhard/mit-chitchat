import webapp2
import jinja2
import os
import re
import logging
from google.appengine.ext import ndb
from google.appengine.api import users
from datetime import date, datetime

jinja_environment = jinja2.Environment(loader=
    jinja2.FileSystemLoader(os.path.dirname(__file__)))


def RenderTemplate(template_file, values={}):
    template = jinja_environment.get_template(template_file)
    
    return template.render(values)


class Account(ndb.Model): 
    """Added from signup"""
    email = ndb.StringProperty(required=False)
    classes = ndb.PickleProperty(required=False)
    user = ndb.UserProperty(required=True)

class Lecture_Post(ndb.Model): 
    """Comments created by a person"""
    user = ndb.UserProperty(required=True)
    mit_class = ndb.StringProperty(required=True)
    date = ndb.DateProperty(required=True)
    professor = ndb.StringProperty(required=True)
    topic = ndb.StringProperty(required=True)
    summary = ndb.StringProperty(required=True)
    rating = ndb.IntegerProperty(required=True)


def Get_Users_Classes():
    usr = Account.query().filter(Account.user==users.get_current_user()).get()
    return usr.classes

class HomeHandler(webapp2.RequestHandler): 
    def get(self):
        user = users.get_current_user()
        account = Account.query().filter(Account.user==user).get()
        if not account: 
            new_user = Account(user=user, 
                                email=user.email(),
                                classes=[])
            new_user.put()
        all_posts = []
        query = Lecture_Post.query().order(-Lecture_Post.date)
        for item in query:
            all_posts.append(item)
        self.response.out.write(RenderTemplate('home.html', 
                                {'all_posts': all_posts,
                                 'usr_classes': Get_Users_Classes()}))

    def post(self):
        dt = datetime.strptime(self.request.get('date'), '%Y-%m-%d')

        new_post = Lecture_Post(user=users.get_current_user(), 
                                mit_class=self.request.get('class'),
                                date=dt,
                                professor=self.request.get('professor'),
                                topic=self.request.get('topic'),
                                summary=self.request.get('summary'),
                                rating=int(self.request.get('rating')))
        new_post.put()
        
        self.redirect('/')


class PostHandler(webapp2.RequestHandler):
    def get(self):
        self.response.out.write(RenderTemplate('post.html',
                                {'date': date.today().isoformat(),
                                 'usr_classes': Get_Users_Classes()}))

class SearchHandler(webapp2.RequestHandler):
    def get(self):
        all_posts = []
        class_query = Lecture_Post.query().order(-Lecture_Post.date).filter(Lecture_Post.mit_class==self.request.get('class').strip())
        for item in class_query:
            all_posts.append(item)
        self.response.out.write(RenderTemplate('home.html',
                                {'all_posts': all_posts,
                                 'usr_classes': Get_Users_Classes()}))
    def post(self):
        usr = Account.query().filter(Account.user==users.get_current_user()).get()
        usr.classes.append(self.request.get('class'))
        usr.put()
        self.redirect('/')

class RemoveClassHandler(webapp2.RequestHandler):
    """Removes a class"""
    def get(self):
        usr = Account.query().filter(Account.user==users.get_current_user()).get()
        usr.classes.remove(self.request.get('class'))
        usr.put()
        self.redirect('/')



routes = [
    ('/remove', RemoveClassHandler),
    ('/', HomeHandler),
    ('/post', PostHandler),
    ('/class', SearchHandler),
]

app = webapp2.WSGIApplication(routes, debug=True)
