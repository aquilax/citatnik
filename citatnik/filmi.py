import cgi
import os

from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext import db
from google.appengine.ext.webapp import template

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
  def get(self):
    quotes = db.GqlQuery("SELECT * FROM Quote ORDER BY date DESC")
    template_values = {
			'quotes': quotes
      }
    path = os.path.join(os.path.dirname(__file__), 'index.html')
    self.response.out.write(template.render(path, template_values))

class AddQuote(webapp.RequestHandler):
  def get(self):
		movies = db.GqlQuery("SELECT * FROM Movie ORDER BY title")
		template_values = {
			'movies': movies
		}
		path = os.path.join(os.path.dirname(__file__), 'add.html')
		self.response.out.write(template.render(path, template_values))

  def post(self):
		if len(self.request.get('movie')) = 0:
			movie = Movie()
    quote = Quote()
    if users.get_current_user():
      quote.user = users.get_current_user()
    quote.movie = self.request.get('movie')
    quote.quote = self.request.get('quote')
    quote.rating = 0
    quote.visible = False
    quote.put()
    self.redirect('/')
   
application = webapp.WSGIApplication(
                                     [('/', MainPage),
                                     ('/add', AddQuote)], 
                                     debug=True)

def main():
  run_wsgi_app(application)

if __name__ == "__main__":
  main()
