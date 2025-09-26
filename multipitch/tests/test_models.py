from django.test import TestCase
from django.db import IntegrityError
from multipitch.models import UserAuth, UserBackup

class UserAuthModelTest(TestCase):

    def test_user_creation(self):
        user = UserAuth.objects.create_user(
            username='alice',
            email='alice@example.com',
            password='password123'
        )
        self.assertEqual(user.username, 'alice')
        self.assertIsNotNone(user.created_at)
        self.assertIsNotNone(user.updated_at)

    def test_updated_at_changes_on_save(self):
        user = UserAuth.objects.create_user(username='bob', password='123')
        old_updated = user.updated_at
        user.save()
        self.assertNotEqual(user.updated_at, old_updated)


class UserBackupModelTest(TestCase):

    def setUp(self):
        self.user = UserAuth.objects.create_user(username='testuser', password='123')

    def test_backup_creation(self):
        blob = b"dummy sqlite"
        backup = UserBackup.objects.create(user=self.user, sqlite_blob=blob)
        self.assertEqual(backup.user, self.user)
        self.assertEqual(backup.sqlite_blob, blob)
        self.assertIsNotNone(backup.last_sync)

    def test_str_method(self):
        blob = b"dummy sqlite"
        backup = UserBackup.objects.create(user=self.user, sqlite_blob=blob)
        self.assertIn(self.user.username, str(backup))

    def test_one_to_one_constraint(self):
        blob1 = b"backup1"
        UserBackup.objects.create(user=self.user, sqlite_blob=blob1)
        blob2 = b"backup2"
        with self.assertRaises(IntegrityError):
            UserBackup.objects.create(user=self.user, sqlite_blob=blob2)
