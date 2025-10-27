import base64
from rest_framework import serializers
from multipitch.models import UserBackup

class UserBackupSerializer(serializers.ModelSerializer):
    sqlite_blob = serializers.CharField()

    class Meta:
        model = UserBackup
        fields = ['sqlite_blob', 'last_sync']
        read_only_fields = ['last_sync']

    def validate_sqlite_blob(self, value):
        if not value:
            raise serializers.ValidationError("Backup file cannot be empty.")
        try:
            return base64.b64decode(value)
        except Exception:
            raise serializers.ValidationError("Invalid Base64 data.")

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['sqlite_blob'] = base64.b64encode(instance.sqlite_blob).decode('utf-8')
        data['last_sync'] = instance.last_sync.isoformat() if instance.last_sync else None
        return data

