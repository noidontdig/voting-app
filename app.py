import os
import cgi
import datetime
import urllib
import wsgiref.handlers

from google.appengine.ext import db
from google.appengine.ext import webapp
from google.appengine.api import users
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext.webapp import template

class Category(db.Model):
  author = db.StringProperty()
  name = db.StringProperty()
  date = db.DateTimeProperty(auto_now_add=True)

class Item(db.Model):
  content = db.StringProperty()
  category = db.ReferenceProperty(Category, collection_name='items')
  votes = db.IntegerProperty()

def category_key(category_id):
  return db.Key.from_path('Category', int(category_id))

class MainPage(webapp.RequestHandler):
  def get(self):
    #category_name=self.request.get('category_name')
    category_query = Category.all().order('-date')
    categories = category_query.fetch(10)

    if users.get_current_user():
        url = users.create_logout_url(self.request.uri)
        url_linktext = 'Logout'
    else:
        url = users.create_login_url(self.request.uri)
        url_linktext = 'Login'


    template_values = {
        'categories': categories,
        'url': url,
        'url_linktext': url_linktext,
    }

    path = os.path.join(os.path.dirname(__file__), 'index.html')
    self.response.out.write(template.render(path, template_values))

class Create(webapp.RequestHandler):
  def get(self):

    if users.get_current_user():
        url = users.create_logout_url(self.request.uri)
        url_linktext = 'Logout'
    else:
        url = users.create_login_url(self.request.uri)
        url_linktext = 'Login'

    template_values = {
        'url': url,
        'url_linktext': url_linktext,
 
    }

    path = os.path.join(os.path.dirname(__file__), 'new.html')
    self.response.out.write(template.render(path, template_values))

  def post(self):
    cat_name = self.request.get('category_name')
    category = Category(name=cat_name)
    if users.get_current_user():
      category.author = users.get_current_user().nickname()

    category.put()

    new_item = self.request.get('item')
    Item(category=category,
          content=new_item).put()

    self.redirect('/', MainPage)


class Edit(webapp.RequestHandler):
  def get(self, category_id):

    if users.get_current_user():
        url = users.create_logout_url(self.request.uri)
        url_linktext = 'Logout'
    else:
        url = users.create_login_url(self.request.uri)
        url_linktext = 'Login'

    category = Category.get(category_key(category_id))

    template_values = {
        'category': category,
        'url': url,
        'url_linktext': url_linktext,
     }
  
    path = os.path.join(os.path.dirname(__file__), 'edit.html')
    self.response.out.write(template.render(path, template_values))

  def post(self):

    category_id = self.request.get('category_id')
    category = Category.get(category_key(category_id))

    new_item = self.request.get('item')
    Item(category=category,
         content=new_item).put()
    self.redirect("/edit/%s" % category_id)

class Delete(webapp.RequestHandler):
  def get(self, thing_id):
    cat = Category.get(category_key(thing_id))
    item = Item.get(item_key(thing_id))
    if cat:
      cat.delete()
      self.redirect('/', MainPage)
    if item:
      item_category = item.category
      category_id = item_category.key().id()
      item.delete()
      self.redirect("/edit/%s" % category_id)


def item_key(item_id):
  return db.Key.from_path('Item', int(item_id))

class Results(webapp.RequestHandler):
  def get(self):

    if users.get_current_user():
        url = users.create_logout_url(self.request.uri)
        url_linktext = 'Logout'
    else:
        url = users.create_login_url(self.request.uri)
        url_linktext = 'Login'

    results = "results"
    template_values = {
        'results' : results,
        'url': url,
        'url_linktext': url_linktext,
    }

    path = os.path.join(os.path.dirname(__file__), 'results.html')
    self.response.out.write(template.render(path, template_values))

    


application = webapp.WSGIApplication(
                      [('/', MainPage),
                       ('/new', Create),
                       ('/edit', Edit),
                       (r'/edit/(.*)', Edit),
                       (r'/delete/(.*)', Delete),
                       ('/results', Results)],
                       debug=True)


def main():
  run_wsgi_app(application)

if __name__ == "__main__":
  main()  



