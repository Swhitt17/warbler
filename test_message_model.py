import os
from unittest import TestCase
from sqlalchemy import exc

from models import db, User, Message, Likes


os.environ['DATABASE_URL'] = "postgresql:///warbler_test"


from app import app


db.create_all()


class MessageModelTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        db.drop_all()
        db.create_all()

        self.uid = 65664
        u1 = User.signup("testuser", "test1@gmail.com", "testing1",None)
        u1id = 987
        u1.id = self.uid

        db.session.commit()

        self.u = User.query.get(self.uid)
       
        self.client = app.test_client()

    def tearDown(self):
            res = super().tearDown()
            db.session.rollback()
            return res
    
    def test_message_model(self):
         
        msg = Message(
              text = "test test 123",
              user_id = self.uid
         )
        
        db.session.add(msg)
        db.session.commit()

        self.assertEqual(len(self.u.messages), 1)
        self.assertEqual(self.u.messages[0].text, "test test 123")
        
       


    def test_message_likes(self):

        msg = Message(
              text = "test test 123",
              user_id = self.uid
         )

        msg2 = Message(
             text = "test message",
             user_id = self.uid
        )

        user = User.signup("jkl", "test5@gmail.com", "testing1", None)
        user_id = 987
        user.id = user_id

        db.session.add_all([msg,msg2,user])
        db.session.commit()

        user.likes.append(msg)

        db.session.commit()

        like = Likes.query.filter(Likes.user_id == user.id).all()
        self.assertEqual(len(like), 1)
        self.assertEqual(like[0].message_id, msg.id) 