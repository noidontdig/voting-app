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

    template_values = {

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

    category = Category.get(category_key(category_id))

    template_values = {
        'category': category,
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



def item_key(item_id):
  return db.Key.from_path('Item', item_name)

class Results(webapp.RequestHandler):
  def get(self):

    results = "results"
    template_values = {
        'results' : results,
    }

    path = os.path.join(os.path.dirname(__file__), 'results.html')
    self.response.out.write(template.render(path, template_values))

    


application = webapp.WSGIApplication(
                      [('/', MainPage),
                       ('/new', Create),
                       ('/edit', Edit),
                       ('/edit/(.*)', Edit),
                       ('/results', Results)],
                       debug=True)


def main():
  run_wsgi_app(application)

if __name__ == "__main__":
  main()  



