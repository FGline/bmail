from google.appengine.ext import ndb

class Message(ndb.Model):
    recipient = ndb.StringProperty()
    subject = ndb.StringProperty()
    content = ndb.TextProperty()
    creation = ndb.DateTimeProperty(auto_now_add=True)
    sender = ndb.StringProperty()


class User(ndb.Model):
    ime = ndb.StringProperty()
    priimek = ndb.StringProperty()
    email = ndb.StringProperty()
    geslo = ndb.StringProperty()