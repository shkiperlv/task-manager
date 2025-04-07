import unittest
from app import app, db
from models import User, Task

class TaskManagerTestCase(unittest.TestCase):
    def setUp(self):
        # Testa konfigurācija ar atmiņas datubāzi
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        self.app = app.test_client()
        self.app_context = app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        # Notīram vidi pēc katra testa
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_register_user(self):
        # Reģistrācijas testa gadījums
        response = self.app.post('/register', data=dict(
            email='test@example.com',
            password='password123'
        ), follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        user = User.query.filter_by(email='test@example.com').first()
        self.assertIsNotNone(user)

    def test_add_task(self):
        # Lietotāja izveide un pieslēgšanās
        user = User(email='test@example.com')
        user.set_password('password123')
        db.session.add(user)
        db.session.commit()

        with self.app as client:
            client.post('/login', data=dict(
                email='test@example.com',
                password='password123'
            ), follow_redirects=True)

            # Uzdevuma pievienošana
            response = client.post('/add', data=dict(
                content='Test Task',
                date='06.04.2025',
                time='10:00'
            ), follow_redirects=True)

            task = Task.query.filter_by(content='Test Task').first()
            self.assertIsNotNone(task)
            self.assertEqual(task.content, 'Test Task')

    def test_delete_task(self):
        # Lietotāja un uzdevuma izveide
        user = User(email='test@example.com')
        user.set_password('password123')
        db.session.add(user)
        db.session.commit()

        task = Task(content='Test Task', user_id=user.id)
        db.session.add(task)
        db.session.commit()

        with self.app as client:
            client.post('/login', data=dict(
                email='test@example.com',
                password='password123'
            ), follow_redirects=True)

            # Uzdevuma dzēšana
            response = client.get(f'/delete/{task.id}', follow_redirects=True)
            self.assertEqual(response.status_code, 200)

            task = db.session.get(Task, task.id)
            self.assertIsNone(task)

if __name__ == '__main__':
    # Saglabā testa rezultātus failā
    with open('test_results.txt', 'w') as f:
        runner = unittest.TextTestRunner(stream=f, verbosity=2)
        unittest.main(testRunner=runner, exit=False)
