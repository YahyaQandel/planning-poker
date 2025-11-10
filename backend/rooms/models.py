import uuid
import secrets
import string
from datetime import datetime
from django.db import models
from django.utils import timezone


def generate_room_code():
    """Generate a random 6-character room code"""
    return ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(6))


def generate_session_name():
    """Generate default session name with today's date"""
    today = datetime.now().strftime("%B %d, %Y")
    return f"Planning Session For {today}"


class Room(models.Model):
    code = models.CharField(max_length=6, unique=True, default=generate_room_code, db_index=True)
    session_name = models.CharField(max_length=255, default=generate_session_name)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    current_story = models.ForeignKey('Story', on_delete=models.SET_NULL, null=True, blank=True, related_name='active_in_room')

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Room {self.code}"


class Participant(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='participants')
    username = models.CharField(max_length=50)
    session_id = models.CharField(max_length=100, unique=True)
    connected = models.BooleanField(default=True)
    joined_at = models.DateTimeField(auto_now_add=True)
    last_seen = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['joined_at']
        unique_together = [['room', 'username']]

    def __str__(self):
        return f"{self.username} in {self.room.code}"


class Story(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='stories')
    story_id = models.CharField(max_length=100, blank=True, null=True)
    title = models.CharField(max_length=255, blank=True, null=True)
    final_points = models.CharField(max_length=10, blank=True, null=True)
    estimated_at = models.DateTimeField(null=True, blank=True)
    order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order', 'created_at']
        verbose_name_plural = 'Stories'

    def __str__(self):
        display = self.story_id or self.title or 'Untitled'
        return f"{display} in {self.room.code}"


class Vote(models.Model):
    VOTE_CHOICES = [
        ('0', '0'),
        ('1', '1'),
        ('2', '2'),
        ('3', '3'),
        ('5', '5'),
        ('8', '8'),
        ('13', '13'),
        ('21', '21'),
        ('?', '?'),
        ('coffee', '☕'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='votes')
    participant = models.ForeignKey(Participant, on_delete=models.CASCADE, related_name='votes')
    story = models.ForeignKey(Story, on_delete=models.CASCADE, related_name='votes')
    value = models.CharField(max_length=10, choices=VOTE_CHOICES)
    revealed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['created_at']
        unique_together = [['participant', 'story']]

    def __str__(self):
        return f"{self.participant.username} voted {self.value} for {self.story}"
