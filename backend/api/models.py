from django.db import models
from django.contrib.auth.models import User


class Note(models.Model):
    """
    Model to store user notes with links to txt files.
    """
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notes')
    title = models.CharField(max_length=200)
    file_path = models.CharField(max_length=500)  # Path to the txt file
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} by {self.author.username}"
