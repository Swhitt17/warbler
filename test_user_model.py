"""User model tests."""

# run these tests like:
#
#    python -m unittest test_user_model.py


import os
from unittest import TestCase
from sqlalchemy import exc

from models import db, User, Message, Follows

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler_test"


# Now we can import app

from app import app

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()


class UserModelTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        db.drop_all()
        db.create_all()

        u1 = User.signup("jkl", "test1@gmail.com", "testing1", None)
        uid1 = 987
        u1.id = uid1

        u2 = User.signup("stu", "test2@gmail.com", "testing2", None)
        uid2 = 654
        u2.id = uid2

        db.session.commit()

        u1 = User.query.get(uid1)
        u2 = User.query.get(uid2)

        self.u1 = u1
        self.uid1 = uid1
        self.u2 = u2
        self.uid2 = uid2

    
        self.client = app.test_client()

    def tearDown(self):
            res = super().tearDown()
            db.session.rollback()
            return res



    def test_user_model(self):
        """Does basic model work?"""

        u = User(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )

        db.session.add(u)
        db.session.commit()

        # User should have no messages & no followers
        self.assertEqual(len(u.messages), 0)
        self.assertEqual(len(u.followers), 0)


    def test_user_following(self):
         self.u1.following.append(self.u2)
         db.session.commit()

         self.assertEqual(len(self.u2.following), 0)
         self.assertEqual(len(self.u2.followers), 1)
         self.assertEqual(len(self.u1.following), 1)
         self.assertEqual(len(self.u1.followers), 0)

         self.assertEqual(self.u2.followers[0].id, self.u1.id)
         self.assertEqual(self.u1.following[0].id, self.u2.id)


    def test_is_following(self):
         
        self.u1.following.append(self.u2)
        db.session.commit() 

        self.assertTrue(self.u1.is_following(self.u2))
        self.assertFalse(self.u2.is_following(self.u1))


    def test_is_followed_by(self):
         
        self.u1.following.append(self.u2)
        db.session.commit() 

        self.assertTrue(self.u2.is_followed_by(self.u1))
        self.assertFalse(self.u1.is_followed_by(self.u2))





def test_valid_signup(self):
     
    user = self.testuser = User.signup("testuser","test@test.com","testuser", None)                          
    userid = 9680
    user.id = userid
    db.session.commit()


    user = User.query.get(userid)
    self.assertIsNone(user)
    self.assertEqual(user.username, "testuser")
    self.assertEqual(user.email, "test@test.com")
    self.assertNotEqual(user.password, "testuser")
    self.assertTrue(user.password.startswith("$2b$"))


def test_invalid_username(self):
     invalid_user = self.testuser = User.signup(None,"test@test.com","testuser", None) 
     userid = 90034
     invalid_user.id = userid
     with self.assertRaises(exc. IntegrityError) as context:
         db.session.commit()

def test_invalid_email(self):
     invalid_user = self.testuser = User.signup("testuser",None,"testuser", None) 
     userid = 90034
     invalid_user.id = userid
     with self.assertRaises(exc. IntegrityError) as context:
         db.session.commit()

def test_invalid_password(self):
     with self.assertRaises(ValueError) as context:
          User.signup("testuser","test@test.com", " ", None)

     with self.assertRaises(ValueError) as context:
          User.signup("testuser","test@test.com", None, None)




def test_good_authenication(self):
     user = User.authenticate(self.u1.username,"password") 
     self.assertNotNone(user)
     self.assertEqual(user.id, self.uid1)

def test_wrong_username(self):
     self.assertFalse(User.authenticate("badusername","password"))

def test_wrong_password(self):
     self.assertFalse(User.authenticate(self.u1.username,"badpassword"))



    

