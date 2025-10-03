from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from multipitch.models import UserBackup
from multipitch.serializers.backup_serializers import UserBackupSerializer
import base64

class BackupUploadView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """
        Save or replace the current user's backup.
        Expects Base64-encoded string in 'sqlite_blob'.
        """
        serializer = UserBackupSerializer(data=request.data)
        if serializer.is_valid():
            backup, created = UserBackup.objects.update_or_create(
                user=request.user,
                defaults={'sqlite_blob': serializer.validated_data['sqlite_blob']}
            )
            return Response({
                "success": True,
                "message": "Backup saved successfully.",
                "last_sync": backup.last_sync
            }, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class BackupRetrieveView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        Retrieve the current user's backup.
        Returns Base64-encoded string in 'sqlite_blob'.
        """
        try:
            backup = request.user.data  # related_name="data"
        except UserBackup.DoesNotExist:
            return Response({"detail": "No backup found."}, status=status.HTTP_404_NOT_FOUND)

        # Encode raw bytes to Base64 for JSON transport
        data = {
            "sqlite_blob": base64.b64encode(backup.sqlite_blob).decode(),
            "last_sync": backup.last_sync
        }
        return Response(data, status=status.HTTP_200_OK)
