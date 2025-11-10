from rest_framework import serializers
from .models import Room, Participant, Story, Vote


class ParticipantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Participant
        fields = ['id', 'username', 'connected', 'joined_at', 'last_seen']
        read_only_fields = ['id', 'joined_at', 'last_seen']


class VoteSerializer(serializers.ModelSerializer):
    participant_name = serializers.CharField(source='participant.username', read_only=True)

    class Meta:
        model = Vote
        fields = ['id', 'participant', 'participant_name', 'value', 'revealed', 'created_at']
        read_only_fields = ['id', 'created_at']


class StorySerializer(serializers.ModelSerializer):
    votes = VoteSerializer(many=True, read_only=True)
    votes_count = serializers.SerializerMethodField()

    class Meta:
        model = Story
        fields = ['id', 'story_id', 'title', 'final_points', 'estimated_at', 'order', 'votes', 'votes_count', 'created_at']
        read_only_fields = ['id', 'created_at']

    def get_votes_count(self, obj):
        return obj.votes.count()


class RoomSerializer(serializers.ModelSerializer):
    participants = ParticipantSerializer(many=True, read_only=True)
    stories = StorySerializer(many=True, read_only=True)
    current_story_data = StorySerializer(source='current_story', read_only=True)
    participants_count = serializers.SerializerMethodField()

    class Meta:
        model = Room
        fields = ['code', 'created_at', 'updated_at', 'current_story', 'current_story_data', 'participants', 'stories', 'participants_count']
        read_only_fields = ['code', 'created_at', 'updated_at']

    def get_participants_count(self, obj):
        return obj.participants.filter(connected=True).count()


class CreateRoomSerializer(serializers.Serializer):
    story_id = serializers.CharField(required=False, allow_blank=True)
    title = serializers.CharField(required=False, allow_blank=True)


class JoinRoomSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=50, required=True)
    session_id = serializers.CharField(max_length=100, required=True)
