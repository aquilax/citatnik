# -*- coding: utf-8 -*-

from google.appengine.api import users
from google.appengine.ext import db
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp.util import run_wsgi_app
from django.core.paginator import ObjectPaginator, InvalidPage
import os

class Movie(db.Model):
	title = db.StringProperty()
	year = db.StringProperty()
	description = db.StringProperty(multiline=True)
	imdb = db.StringProperty()
	visible = db.BooleanProperty(default=False)

class Quote(db.Model):
	movie = db.ReferenceProperty(Movie)
	quote = db.StringProperty(multiline=True)
	author = db.UserProperty()
	rating = db.RatingProperty(default=0)
	visible = db.BooleanProperty(default=False)
	date = db.DateTimeProperty(auto_now_add=True)

class MainPage(webapp.RequestHandler):
  """Main page"""
  def get(self):
    """Main page dafault action"""
    #quotes = db.GqlQuery("SELECT * FROM Quote WHERE visible = True ORDER BY date DESC")
    quotes = db.Query(Quote)
    quotes.filter('visible = ', True)
    quotes.order('-date')
    movies = db.Query(Movie)
    movies.order('year')

    paginator = ObjectPaginator(quotes, 10)

    if (self.request.get('page')):
      try:
        page = int(self.request.get('page'))
      except:
        page = 0
    else:
      page = 0
    
    if (paginator.pages < page):
      page = 0

    items = paginator.get_page(page)

    if users.get_current_user():
      url = users.create_logout_url(self.request.uri)
      url_linktext = 'Изход'
    else:
      url = users.create_login_url(self.request.uri)
      url_linktext = 'Вход'

    admin = False
    if users.is_current_user_admin():
      admin = True

    template_values = {
      'quotes': items,
      'movies': movies,
      'url': url,
      'url_linktext': url_linktext,
      'admin': admin,
      'paged': True,
      'has_next': paginator.has_next_page(page),
      'has_prev': paginator.has_previous_page(page),
      'page': int(page)+1,
      'prev': int(page)-1,
      'first': (page == 0)
      }
    path = os.path.join(os.path.dirname(__file__), 'index.html')
    self.response.out.write(template.render(path, template_values))

class AddQuote(webapp.RequestHandler):
  def get(self):
		movies = db.GqlQuery("SELECT * FROM Movie WHERE visible = True ORDER BY title")
		template_values = {
			'movies': movies
		}
		path = os.path.join(os.path.dirname(__file__), 'add.html')
		self.response.out.write(template.render(path, template_values))

  def post(self):
    if (len(self.request.get('movie')) != 0):
      movie = Movie()
      movie.title = self.request.get('movie')
      movie.put()
    else:
      movie = db.get(self.request.get('mid'))
    quote = Quote()
    if users.get_current_user():
      quote.user = users.get_current_user()
    quote.movie = movie
    quote.quote = self.request.get('quote')
    quote.rating = 0
    quote.visible = False
    quote.put()
    self.redirect('/')

class MoviePage(webapp.RequestHandler):
  def get(self):
    mid = self.request.get('mid')
    movie = db.get(mid)
    quotes = db.Query(Quote)
    quotes.filter('movie =', movie);
    quotes.filter('visible = ', True)
    if users.get_current_user():
      url = users.create_logout_url(self.request.uri)
      url_linktext = 'Изход'
    else:
      url = users.create_login_url(self.request.uri)
      url_linktext = 'Вход'
    admin = False
    if users.is_current_user_admin():
      admin = True

    template_values = {
      'quotes': quotes,
      'movie': movie,
      'url': url,
      'url_linktext': url_linktext,
      'admin': admin
      }
    path = os.path.join(os.path.dirname(__file__), 'index.html')
    self.response.out.write(template.render(path, template_values))

class Admin(webapp.RequestHandler):
  def get(self):
    if users.is_current_user_admin():
      quotes = db.GqlQuery("SELECT * FROM Quote WHERE visible = False ORDER BY date DESC")
      if users.get_current_user():
        url = users.create_logout_url(self.request.uri)
        url_linktext = 'Изход'
      else:
        url = users.create_login_url(self.request.uri)
        url_linktext = 'Вход'

      admin = False
      if users.is_current_user_admin():
        admin = True

      template_values = {
        'quotes': quotes,
        'url': url,
        'url_linktext': url_linktext,
        'admin': admin
        }
      path = os.path.join(os.path.dirname(__file__), 'admin.html')
      self.response.out.write(template.render(path, template_values))
    else:
      self.redirect('/')

class Moderate(webapp.RequestHandler):
  def get(self):
    if not users.is_current_user_admin():
      self.redirect('/')
    qid = self.request.get('qid')
    movies = db.GqlQuery("SELECT * FROM Movie ORDER BY title")
    quote = db.get(qid)
    template_values = {
      'movies': movies,
      'quote': quote,
      'qid': qid
    }
    path = os.path.join(os.path.dirname(__file__), 'moderate.html')
    self.response.out.write(template.render(path, template_values))

  def post(self):
    if not users.is_current_user_admin():
      self.redirect('/')
    mid = self.request.get('mid')
    if (mid == 0):
      movie = Movie()
      movie.title = self.request.get('movie')
      movie.visible = True
      movie.put()
    else:
      movie = db.get(self.request.get('mid'))
      movie.visible = True
      movie.put()
    quote = db.get(self.request.get('qid'));
    quote.movie = movie
    quote.quote = self.request.get('quote')
    quote.rating = 0
    quote.visible = True
    quote.put()
    self.redirect('/admin')

application = webapp.WSGIApplication(
  [('/', MainPage),
  ('/add', AddQuote),
  ('/admin', Admin),
  ('/moderate', Moderate),
  ('/movie', MoviePage),
  ],
  debug=True)

def main():
  run_wsgi_app(application)

if __name__ == "__main__":
  main()