from rest_framework import viewsets
from .models import DeploymentEvent
from .serializers import DeploymentEventSerializer


class DeploymentEventViewSet(viewsets.ModelViewSet):
    """
    Full CRUD for deployment events.
    - POST: deploy.py reports a new event after every run
    - GET: the dashboard reads history from here
    We're not restricting to read-only because deploy.py itself
    needs to create records — auth/permissions can be tightened
    later once this moves off localhost.
    """
    queryset = DeploymentEvent.objects.all()
    serializer_class = DeploymentEventSerializer