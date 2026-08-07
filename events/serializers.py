from rest_framework import serializers
from .models import DeploymentEvent


class DeploymentEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeploymentEvent
        fields = ["id", "git_sha", "status", "reason", "timestamp"] 