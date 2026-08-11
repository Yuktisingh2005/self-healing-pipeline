from django.db import models


class DeploymentEvent(models.Model):
    """
    One row per deploy attempt. This is the single source of truth
    the dashboard reads from — deploy.py POSTs here at the end of
    every run, whether it promoted or rolled back.
    """

    STATUS_CHOICES = [
        ("promoted", "Promoted"),
        ("rolled_back", "Rolled Back"),
    ]

    git_sha = models.CharField(max_length=40)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    reason = models.TextField(blank=True, null=True)  # e.g. db_error from health check
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-timestamp"] 

    def __str__(self):
        return f"{self.git_sha} - {self.status} at {self.timestamp}"