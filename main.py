#!/usr/bin/env python

import os
import jinja2
import webapp2
from models import Message
import cgi
import json
from google.appengine.api import urlfetch
from google.appengine.api import users


template_dir = os.path.join(os.path.dirname(__file__), "templates")
jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir), autoescape=False)


class BaseHandler(webapp2.RequestHandler):

    def write(self, *args, **kwargs):
        return self.response.out.write(*args, **kwargs)

    def render_str(self, template, **params):
        template = jinja_env.get_template(template)
        return template.render(params)

    def render(self, template, **kwargs):
        return self.write(self.render_str(template, **kwargs))

    def render_template(self, view_filename, params=None):
        if params is None:
            params = {}
        template = jinja_env.get_template(view_filename)
        return self.response.out.write(template.render(params))


class MainHandler(BaseHandler):
    def get(self):
        user = users.get_current_user()
        if user:
            logiran = True
            logout_url = users.create_logout_url('/')
            params = {"logiran":logiran, "logout_url":logout_url, "user":user}

        else:
            logiran = False
            login_url = users.create_login_url('/')

            params = {"logiran": logiran, "login_url": login_url, "user": user}
        return self.render_template("hello.html", params)


class SendMessageHandler(BaseHandler):
    def get(self):
        logiran = True
        params = {"logiran": logiran}
        return self.render_template("send_message.html", params=params)

    def post(self):
        recipient = self.request.get("recipient")
        subject = self.request.get("subject")
        content = self.request.get("content")
        user = users.get_current_user() # Save sender in model Message
        sender = user.nickname()
        save_user = str(sender)

        message= Message(sender=save_user, recipient=recipient, subject=subject, content=content) # Create Message
        message.put()  # Save in DataStore
        params = {"recipient": recipient, "subject": subject, "content": content}
        return self.render_template("send_message.html", params=params)


class ReceivedMessagesHandler(BaseHandler):
    def get(self):
        user = users.get_current_user()
        # if not user:
        #     self.redirect_to("main")
        user_nickname=str(user.nickname())
        received_messages = Message.query(Message.recipient == user_nickname).fetch()

        params = {"received_messages": received_messages}
        return self.render_template("inbox.html", params=params)


class InboxMessagesHandler(BaseHandler):
    def get(self):
        user = users.get_current_user()
        user_nickname=str(user.nickname())
        sent_messages = Message.query(Message.sender == user_nickname).fetch()
        params = {"sent_messages": sent_messages}
        return self.render_template("sent_mail.html", params=params)


class MessageHandler(BaseHandler):
    def get(self, message_id):
        action = ""
        message = Message.get_by_id(int(message_id))
        # if message.umaknjeno:
        #     action = "obnovi"
        # else:
        #     action = "zakljuci"
        params = {"message": message, "action": action}
        return self.render_template("message.html", params=params)


class DeleteMessageHandler(BaseHandler):
    def get(self, message_id):
        message = Message.get_by_id(int(message_id))
        params = {"message": message}
        return self.render_template("delete_message.html", params=params)

    def post(self, message_id):
        message = Message.get_by_id(int(message_id))
        message.key.delete()
        return self.redirect_to("received")

class WeatherHandler(BaseHandler):
    def get(self):
        url = "http://api.openweathermap.org/data/2.5/weather?q=London,uk&units=metric&appid=2a80aaca48e4d7c2f862643e3461e64d"

        result = urlfetch.fetch(url)
        podatki=json.loads(result.content)
        user = users.get_current_user()
        logiran = False
        if user:
            logiran = True
        params = {"podatki":podatki,
                  "logiran": logiran}


        self.render_template("weather.html", params=params)


app = webapp2.WSGIApplication([
    webapp2.Route('/', MainHandler, name="main"),
    webapp2.Route('/message', SendMessageHandler),
    webapp2.Route('/received', ReceivedMessagesHandler, name="received"),
    webapp2.Route('/sent_mail', InboxMessagesHandler),
    webapp2.Route('/message/<message_id:\d+>/delete', DeleteMessageHandler),
    webapp2.Route('/message/<message_id:\d+>', MessageHandler),
    webapp2.Route('/weather', WeatherHandler),
], debug=True)