import base64
from rest_framework import serializers
from multipitch.models import UserBackup

class UserBackupSerializer(serializers.ModelSerializer):
    # Accept Base64 string from frontend
    sqlite_blob = serializers.CharField()

    class Meta:
        model = UserBackup
        fields = ['sqlite_blob', 'last_sync']
        read_only_fields = ['last_sync']

    def validate_sqlite_blob(self, value):
        if not value:
            raise serializers.ValidationError("Backup file cannot be empty.")
        try:
            # Decode Base64 into bytes for BinaryField
            return base64.b64decode(value)
        except Exception:
            raise serializers.ValidationError("Invalid Base64 data.")
