import os
import cgi
import datetime
import urllib
import wsgiref.handlers

from random import sample
from google.appengine.ext import db
from google.appengine.ext import webapp
from google.appengine.api import users
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext.webapp import template
from xml.dom.minidom import parse, parseString

class Category(db.Model):
  author = db.StringProperty()
  name = db.StringProperty()
  date = db.DateTimeProperty(auto_now_add=True)

class Item(db.Model):
  content = db.StringProperty()
  category = db.ReferenceProperty(Category, collection_name='items')
  votes = db.IntegerProperty()
  losses = db.IntegerProperty()
  percent_win = db.IntegerProperty()

def category_key(category_id):
  return db.Key.from_path('Category', int(category_id))


class MainPage(webapp.RequestHandler):
  def get(self):
    
    categories = Category.all()   

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

    isCreate = self.request.get('create')
    isImport = self.request.get('import')
    if isCreate:
      cat_name = self.request.get('category_name')
      category = Category(name=cat_name)
      if users.get_current_user():
        category.author = users.get_current_user().nickname()

      category.put()

      new_item = self.request.get('item')
      Item(category=category,
            content=new_item,
            votes=0, losses=0, percent_win=0).put()

    else:
      document = parseString(self.request.POST.multi['import_category'].file.read())
      tree = document.documentElement
      cat_name = str(tree.getElementsByTagName('NAME')[0].firstChild.nodeValue)
      category = Category(name=cat_name)
      if users.get_current_user():
        category.author = users.get_current_user().nickname()
      category.put()
      items = []
      for item in tree.getElementsByTagName('NAME')[1:]:
        items.append(str(item.firstChild.nodeValue))
      for item in items:
        Item(content=item, 
          category=category,
          votes=0, losses=0, percent_win=0).put()


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
      
    if (users.get_current_user() 
      and users.get_current_user().nickname() == category.author):
      template_values = {
        'category': category,
        'url': url,
        'url_linktext': url_linktext,
      }

    else: 

      error = "You do not have permission to edit this category"
      template_values = {
        'error': error,
      }
    
    path = os.path.join(os.path.dirname(__file__), 'edit.html')
    self.response.out.write(template.render(path, template_values))

  def post(self):

    isEdit = self.request.get('add_item')
    category_id = self.request.get('category_id')
    category = Category.get(category_key(category_id))

    if isEdit:  
      new_item = self.request.get('item')
      Item(category=category,
           content=new_item,
           votes=0, losses=0, percent_win=0).put()
      self.redirect("/edit/%s" % category_id)

    else:
      document = parseString(self.request.POST.multi['import_category'].file.read())
      tree = document.documentElement
      cat_name = str(tree.getElementsByTagName('NAME')[0].firstChild.nodeValue)
      if cat_name != category.name:
        error = "You Imported the wrong Category"
        category.author = users.get_current_user().nickname()
        template_values = {
        'error': error,
        }
        path = os.path.join(os.path.dirname(__file__), 'edit.html')
        self.response.out.write(template.render(path, template_values))
      else: 
        items = []
        for item in tree.getElementsByTagName('NAME')[1:]:
          items.append(str(item.firstChild.nodeValue))
        for item in items:
          for i in category.items:
            if item == i.content:
              i.delete()
          Item(content=item, 
            category=category,
            votes=0, losses=0, percent_win=0).put()


        self.redirect("/edit/%s" % category_id)

class Delete(webapp.RequestHandler):
  def get(self, thing_id):
    

    cat = Category.get(category_key(thing_id))
    item = Item.get(item_key(thing_id))
    if cat:
      if (users.get_current_user() 
      and users.get_current_user().nickname() == cat.author):
        cat.delete()
        self.redirect('/', MainPage)
      else:
        error = "You do not have permission to delete this category"
        template_values = {
          'error': error,
        }
        path = os.path.join(os.path.dirname(__file__), 'edit.html')
        self.response.out.write(template.render(path, template_values))

    if item:
      if (users.get_current_user() 
      and users.get_current_user().nickname() == item.category.author):
      
        item_category = item.category
        category_id = item_category.key().id()
        item.delete()
        self.redirect("/edit/%s" % category_id)
      else:
        error = "You do not have permission to delete this item"
        template_values = {
          'error': error,
        }
        path = os.path.join(os.path.dirname(__file__), 'edit.html')
        self.response.out.write(template.render(path, template_values))

class Vote(webapp.RequestHandler):
  def get(self, category_id):
    
    category = Category.get(category_key(category_id))
    myObjects = list(category.items)

    if len(myObjects) < 2:
      error = "The category must have at least two items to vote on"
      template_values = {
        'error': error
      }
      path = os.path.join(os.path.dirname(__file__), 'edit.html')
      self.response.out.write(template.render(path, template_values))

    else:
      choose = sample(myObjects, 2)
      
      if users.get_current_user():
          url = users.create_logout_url(self.request.uri)
          url_linktext = 'Logout'
      else:
          url = users.create_login_url(self.request.uri)
          url_linktext = 'Login'

      template_values = {
          'category': category,
          'item1': choose[0],
          'item2': choose[1],
          'url': url,
          'url_linktext': url_linktext,
      }

      path = os.path.join(os.path.dirname(__file__), 'vote.html')
      self.response.out.write(template.render(path, template_values))

  def post(self, category_id):

    category = Category.get(category_key(category_id))
    skip = self.request.get('skip')
    if not skip:
      voted = True
      skipped = False
      pair = self.request.get('pair')
      winner_id = self.request.get('vote')
      items = pair.split(',')
      if winner_id == items[0]:
        loser_id = items[1]
      else:
        loser_id = items[0]

      winner = Item.get(item_key(winner_id))
      loser = Item.get(item_key(loser_id))
      
      winner.votes += 1
      loser.losses += 1
      winner.percent_win = int((winner.votes / (winner.votes + winner.losses + 0.0)) * 100)
      loser.percent_win = int((loser.votes / (loser.votes + loser.losses + 0.0)) * 100)
      winner.put()
      loser.put()

    else:
      voted = False
      skipped = True
      winner = ""
      loser = ""

    myObjects = list(category.items)
    choose = sample(myObjects, 2)

    if users.get_current_user():
        url = users.create_logout_url(self.request.uri)
        url_linktext = 'Logout'
    else:
        url = users.create_login_url(self.request.uri)
        url_linktext = 'Login'

    template_values = {
        'voted': voted,
        'skipped': skipped,
        'category': category,
        'winner': winner,
        'loser': loser,
        'item1': choose[0],
        'item2': choose[1],
        'url': url,
        'url_linktext': url_linktext,
    }

    path = os.path.join(os.path.dirname(__file__), 'vote.html')
    self.response.out.write(template.render(path, template_values))


def item_key(item_id):
  return db.Key.from_path('Item', int(item_id))

class AllResults(webapp.RequestHandler):
  def get(self):

    results = Category.all()
      
    if users.get_current_user():
        url = users.create_logout_url(self.request.uri)
        url_linktext = 'Logout'
    else:
        url = users.create_login_url(self.request.uri)
        url_linktext = 'Login'

    template_values = {
        'results' : results,
        'url': url,
        'url_linktext': url_linktext,
    }

    path = os.path.join(os.path.dirname(__file__), 'results.html')
    self.response.out.write(template.render(path, template_values))

class Results(webapp.RequestHandler):
  def get(self, category_id):

    category = Category.get(category_key(category_id))
    results = [category]
      
    if users.get_current_user():
        url = users.create_logout_url(self.request.uri)
        url_linktext = 'Logout'
    else:
        url = users.create_login_url(self.request.uri)
        url_linktext = 'Login'

    template_values = {
        'results': results,
        'url': url,
        'url_linktext': url_linktext,
    }

    path = os.path.join(os.path.dirname(__file__), 'results.html')
    self.response.out.write(template.render(path, template_values))
  
class Export(webapp.RequestHandler):
  def get(self, category_id):

    category = Category.get(category_key(category_id))
    path = os.path.join(os.path.dirname(__file__), 'export.xml')
    self.response.out.write(template.render(path, {'category': category, 'items': category.items}))
    self.response.headers.add_header("Content-type", 'text/xml')

   

application = webapp.WSGIApplication(
                      [('/', MainPage),
                       ('/new', Create),
                       ('/edit', Edit),
                       (r'/edit/(.*)', Edit),
                       (r'/delete/(.*)', Delete),
                       (r'/vote/(.*)', Vote),
                       (r'/export/(.*)', Export),
                       ('/results', AllResults),
                       (r'/results/(.*)', Results)],
                       debug=True)


def main():
  run_wsgi_app(application)

if __name__ == "__main__":
  main()  



