from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from multipitch.models import UserBackup
import base64

User = get_user_model()


class BackupUploadViewTests(APITestCase):
    def setUp(self):
        self.url = reverse('backup-upload')
        self.user = User.objects.create_user(
            username='backupuser',
            email='backup@example.com',
            password='StrongPass123!'
        )
        # Base64-encoded payload
        self.valid_payload = {'sqlite_blob': base64.b64encode(b'some binary data').decode()}
        self.empty_payload = {'sqlite_blob': ''}

    def test_upload_success_first_time(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post(self.url, self.valid_payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(UserBackup.objects.filter(user=self.user).exists())
        self.assertIn('last_sync', response.data)

    def test_upload_success_overwrite(self):
        UserBackup.objects.create(user=self.user, sqlite_blob=b'old data')
        self.client.force_authenticate(user=self.user)
        response = self.client.post(self.url, self.valid_payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        backup = UserBackup.objects.get(user=self.user)
        self.assertEqual(backup.sqlite_blob, base64.b64decode(self.valid_payload['sqlite_blob']))

    def test_upload_empty_blob(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post(self.url, self.empty_payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('sqlite_blob', response.data)

    def test_upload_unauthenticated(self):
        response = self.client.post(self.url, self.valid_payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class BackupRetrieveViewTests(APITestCase):
    def setUp(self):
        self.url = reverse('backup-download')
        self.user = User.objects.create_user(
            username='backupuser',
            email='backup@example.com',
            password='StrongPass123!'
        )
        self.other_user = User.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='StrongPass123!'
        )
        self.backup_data = b'some data'
        self.backup = UserBackup.objects.create(user=self.user, sqlite_blob=self.backup_data)

    def test_retrieve_existing_backup(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        returned_bytes = base64.b64decode(response.data['sqlite_blob'])
        self.assertEqual(returned_bytes, self.backup.sqlite_blob)

    def test_retrieve_no_backup(self):
        self.client.force_authenticate(user=self.other_user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_retrieve_unauthenticated(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
