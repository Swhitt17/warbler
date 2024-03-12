"""User View Tests"""

import os
from unittest import TestCase


from models import db, connect_db, User, Message, Follows, Likes

os.environ['DATABASE_URL'] = "postgresql:///warbler_test"

from app import app, CURR_USER_KEY

db.create_all()

app.config['WTF_CSRF_ENABLED'] = False


class UserViewTestCase(TestCase):
    """Test views for user."""

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
        self.testuser_id = 968
        self.testuser.id = self.testuser_id

        self.u1 = User.signup("jkl", "test1@gmail.com", "testing1")
        self.u1_id = 987
        self.u1.id = self.u1_id
        self.u2 = User.signup("stu", "test2@gmail.com", "testing2")
        self.u2_id = 654
        self.u2.id = self.u2_id
        self.u3 = User.signup("xyz", "test3@gmail.com", "testing3")
        self.u4 = User.signup("testing", "test4@gmail.com", "testing4")

        db.session.commit()


    def tearDown(self):
            res = super().tearDown()
            db.session.rollback()
            return res


    def test_login(self):

      with self.client as c:
         
         res = c.get('/user/login')
         html = res.get_data(as_text=True)

         self.assertEqual(res.status_code, 200)
         self.AssertIn('<h2>Welcome back </h2>')
           


    def test_signup(self):
        
        with self.client as c:
         
         res = c.get('/user/signup')
         html = res.get_data(as_text=True)

         self.assertEqual(res.status_code, 200)
         self.AssertIn('<h2> Join Warbler today </h2>')


    def test_edit_profile(self):
        with self.client as c:
         
         res = c.get('/user/signup')
         html = res.get_data(as_text=True)

         self.assertEqual(res.status_code, 200)
         self.AssertIn('<h2> Edit Profile </h2>')

    def test_users_index(self):
        with self.client as c:

            res = c.get('/users')

            self.assertIn("@testuser", str(res.data))
            self.assertIn("@jkl", str(res.data))
            self.assertIn("@stu", str(res.data))
            self.assertIn("@xyz", str(res.data))
            self.assertIn("@testing", str(res.data))



    def test_user_show(self):

        with self.client as c:
           
                res = c.get(f'/users/{self.testuser_id}')
            
                self.assertEqual(res.status_code, 200)

                self.assertIn("@testuser", str(res.data))
                

    def setup_followers(self):
        f1 = Follows(user_being_followed_id=self.u1_id, user_following_id=self.testuser_id)
        f2  = Follows(user_being_followed_id=self.u2_id, user_following_id=self.testuser_id)
        f3 = Follows(user_being_followed_id=self.testuser_id, user_following_id=self.u1_id)

        db.session.add_all([f1,f2,f3])
        db.session.commit()


        

    def test_show_following(self):
         self.setup_followers()

         with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            res = c.get(f'/users/{self.testuser_id}/following') 
            self.assertEqual(res.status_code, 200)
            self.assertIn("@jkl", str(res.data))
            self.assertIn("@stu", str(res.data))
            self.assertNotIn("@xyz", str(res.data))
            self.assertNotIn("@testing", str(res.data))



    def test_show_followers(self):
        self.setup_followers()

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id


            res = c.get(f'/users/{self.testuser_id}/followers') 
            self.assertEqual(res.status_code, 200)
            self.assertIn("@jkl", str(res.data))
            self.assertIn("@stu", str(res.data))
            self.assertNotIn("@xyz", str(res.data))
            self.assertNotIn("@testing", str(res.data))


    def test_unathorized_following(self):
        self.setup_followers()

        with self.client as c:

            res = c.get(f'/users/{self.testuser_id}/following', follow_redirects = True) 
            self.assertEqual(res.status_code, 200)
            self.assertNotIn("@jkl", str(res.data))
            self.assertIn( "Access Unauthorized", str(res.data))


    
    def test_unauthorized_followers(self):
        self.setup_followers()

        with self.client as c:

            res = c.get(f'/users/{self.testuser_id}/followers', follow_redirects = True) 
            self.assertEqual(res.status_code, 200)
            self.assertNotIn("@jkl", str(res.data))
            self.assertIn( "Access Unauthorized", str(res.data))


    def setup_likes(self):
        msg = Message(text = "test test 123",user_id = self.testuser_id)
        msg2 = Message(text = "test message",user_id = self.testuser_id)
        msg3 = Message(id=3749, text="like this warble", user_id = self.u1_id)
        db.session.add([msg,msg2,msg3])
        db.session.commit()

        like = Likes(user_id=self.testuser_id, message_id=3731)
        db.session.add(like)
        db.session.commit()

    def test_add_like(self):
       msg = Message(id=4596, text=" plz like this warble", user_id = self.u1_id)
       db.session.add(msg)
       db.session.commit()

       with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            res = c.post(f"/messages/4596/like", follow_redirects=True)
            self.assertEqual(res.status_code,200)

            likes = Likes.query.filter(Likes.message_id == 4596).all()
            self.assertEqual(len(likes),1)
            self.assertEqual(likes[0].user_id, self.testuser_id)

    def test_remove_like(self):        
        self.setup_likes() 

        msg = Message.query.filter(Message.text == "like this warble").one()
        self.assertIsNotNone(msg)
        self.assertNotEqual(msg.user_id, self.testuser_id)

        like = Likes.query.filter(Likes.user_id == self.testuser_id and Likes.message_id==msg.id).one()

        self.assertIsNone(like)


        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            res = c.post(f"/messages/{msg.id}/like", follow_redirects=True)
            self.assertEqual(res.status_code,200)

            likes = Likes.query.filter(Likes.message_id == msg.id).all()
            self.assertEqual(len(likes),0)

    def test_unathenticated_like(self):
        self.setup_likes() 

        msg = Message.query.filter(Message.text == "like this warble").one()
        self.assertIsNotNone(msg)

        like_count = Likes.query.count()

        with self.client as c:
            res = c.post(f"/messages/{msg.id}/like", follow_redirects=True)
            self.assertEqual(res.status_code,200)
            self.assertIn( "Access Unauthorized", str(res.data))
            self.assertIn( like_count, Likes.query.count())








        






       

       




  
         


   