"""Message View tests."""

# run these tests like:
#
#    FLASK_ENV=production python -m unittest test_message_views.py


import os
from unittest import TestCase

from models import db, connect_db, Message, User

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler_test"


# Now we can import app

from app import app, CURR_USER_KEY

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()

# Don't have WTForms use CSRF at all, since it's a pain to test

app.config['WTF_CSRF_ENABLED'] = False


class MessageViewTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        db.drop_all()
        db.create_all()

        User.query.delete()
        Message.query.delete()

        self.client = app.test_client()

        self.testuser = User.signup(username="testuser",
                                    email="test@test.com",
                                    password="testuser",
                                    image_url=None)
        self.testuser_id = 852
        self.testuser.id = self.testuser_id
        
        db.session.commit()

    def test_add_message(self):
        """Can use add a message?"""

        # Since we need to change the session to mimic logging in,
        # we need to use the changing-session trick:

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            # Now, that session setting is saved, so we can have
            # the rest of ours test

            resp = c.post("/messages/new", data={"text": "Hello"})

            # Make sure it redirects
            self.assertEqual(resp.status_code, 302)

            msg = Message.query.one()
            self.assertEqual(msg.text, "Hello")

    def test_no_session(self):
        with self.client as c:
            res = c.post("/messages/new", data={"text": "Hello"}, follows_redirects =True)
            self.assertEqual(res.status_code, 200)
            self.assertIn( "Access Unauthorized", str(res.data))

    def test_unknown_user(self):
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = 9999012

        res = c.post("/messages/new", data={"text": "Hello"}, follows_redirects =True)
        self.assertEqual(res.status_code, 200)
        self.assertIn( "Access Unauthorized", str(res.data))


    def test_messages_show(self):

        msg = Message(
            id = 456,
            text = "test message",
            user_id = self.testuser_id
        )

        db.session.add(msg)
        db.session.commit()

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            msg = Message.query.get(456)

            res = c.get(f'/messages/{msg.id}')

            self.assertEqual(res.status_code, 200)
            self.assertIn(msg.text, str(res.data))
           
    def test_invalid_message_show(self):

         with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

        
            res = c.get('/messages/999999')
            
            self.assertEqual(res.status_code, 404)


    def test_messages_destroy(self):
        """Does the message get deleted"""

        msg = Message(
            id = 456,
            text = "test message",
            user_id = self.testuser_id
        )

        db.session.add(msg)
        db.session.commit()

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            res = c.post("/messages/456/delete", follows_redirects =True)
            self.assertEqual(res.status_code, 200)

            msg = Message.query.get(456)
            self.assertIsNone(msg)


    def test_unathorized_message_destroy(self):
        user = User.signup(username="unathorized-user",
                                    email="test2@test.com",
                                    password="testing",
                                    image_url=None)
        user.id = 10234

         
        msg = Message(
            id = 456,
            text = "test message",
            user_id = self.testuser_id
        )
         
        db.session.add(msg,user)
        db.session.commit()

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = 9999012
            
            res = c.post("/messages/456/delete", follows_redirects =True)
            self.assertEqual(res.status_code, 200)
            self.assertIn( "Access Unauthorized", str(res.data))

            msg = Message.query.get(456)
            self.assertIsNone(msg)


    def test_unknown_user_message_destroy(self):

        msg = Message(
            id = 456,
            text = "test message",
            user_id = self.testuser_id
        )

        db.session.add(msg)
        db.session.commit()

        with self.client as c:
            res = c.post("/messages/456/delete", follows_redirects =True)
            self.assertEqual(res.status_code, 200)
            self.assertIn( "Access Unauthorized", str(res.data))

            msg = Message.query.get(456)
            self.assertIsNone(msg)




