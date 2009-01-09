import cgi
import os

from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext import db
from google.appengine.ext.webapp import template

class Quote(db.Model):
  movie = db.StringProperty()
  quote = db.StringProperty(multiline=True)
  date = db.DateTimeProperty(auto_now_add=True)
  author = db.UserProperty()
  rating = db.RatingProperty(default=0)
  visible = db.BooleanProperty(default=False)

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
    template_values = {}
    path = os.path.join(os.path.dirname(__file__), 'add.html')
    self.response.out.write(template.render(path, template_values))

  def post(self):
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
