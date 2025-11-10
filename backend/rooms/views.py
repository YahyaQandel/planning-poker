from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.utils import timezone
from .models import Room, Participant, Story, Vote
from .serializers import (
    RoomSerializer,
    ParticipantSerializer,
    StorySerializer,
    VoteSerializer,
    CreateRoomSerializer,
    JoinRoomSerializer
)


class RoomViewSet(viewsets.ModelViewSet):
    queryset = Room.objects.all()
    serializer_class = RoomSerializer
    lookup_field = 'code'

    def create(self, request):
        """Create a new room with optional initial story"""
        serializer = CreateRoomSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        room = Room.objects.create()

        # Create initial story if provided
        story_id = serializer.validated_data.get('story_id')
        title = serializer.validated_data.get('title')

        if story_id or title:
            story = Story.objects.create(
                room=room,
                story_id=story_id or '',
                title=title or '',
                order=0
            )
            room.current_story = story
            room.save()

        return Response(RoomSerializer(room).data, status=status.HTTP_201_CREATED)

    def retrieve(self, request, code=None):
        """Get room details"""
        room = get_object_or_404(Room, code=code)
        return Response(RoomSerializer(room).data)

    @action(detail=True, methods=['post'])
    def join(self, request, code=None):
        """Join a room"""
        room = get_object_or_404(Room, code=code)
        serializer = JoinRoomSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        username = serializer.validated_data['username']
        session_id = serializer.validated_data['session_id']

        # Check if participant already exists
        participant, created = Participant.objects.get_or_create(
            room=room,
            username=username,
            defaults={'session_id': session_id, 'connected': True}
        )

        if not created:
            participant.session_id = session_id
            participant.connected = True
            participant.save()

        return Response({
            'participant': ParticipantSerializer(participant).data,
            'room': RoomSerializer(room).data
        })

    @action(detail=True, methods=['post'])
    def add_story(self, request, code=None):
        """Add a new story to estimate"""
        room = get_object_or_404(Room, code=code)

        story_id = request.data.get('story_id', '')
        title = request.data.get('title', '')

        # Get the highest order number
        max_order = Story.objects.filter(room=room).count()

        story = Story.objects.create(
            room=room,
            story_id=story_id,
            title=title,
            order=max_order
        )

        # Set as current story if no current story
        if not room.current_story:
            room.current_story = story
            room.save()

        return Response(StorySerializer(story).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'])
    def reset(self, request, code=None):
        """Reset room - clear all votes for current story"""
        room = get_object_or_404(Room, code=code)

        if room.current_story:
            # Delete all votes for current story
            Vote.objects.filter(room=room, story=room.current_story).delete()

        return Response({'message': 'Room reset successfully'})

    @action(detail=True, methods=['post'])
    def reveal(self, request, code=None):
        """Reveal all votes for current story"""
        room = get_object_or_404(Room, code=code)

        if room.current_story:
            votes = Vote.objects.filter(room=room, story=room.current_story)
            votes.update(revealed=True)

            # Calculate average (excluding ? and coffee)
            numeric_votes = votes.exclude(value__in=['?', 'coffee']).values_list('value', flat=True)
            if numeric_votes:
                # Convert to integers and calculate average
                vote_values = [int(v) for v in numeric_votes]
                average = sum(vote_values) / len(vote_values)
                rounded = round(average)

                # Store both average and rounded value (we'll use rounded as placeholder)
                room.current_story.final_points = str(rounded)
                room.current_story.estimated_at = timezone.now()
                room.current_story.save()

        return Response(RoomSerializer(room).data)

    @action(detail=True, methods=['post'])
    def confirm_points(self, request, code=None):
        """Confirm and finalize story points"""
        room = get_object_or_404(Room, code=code)
        points = request.data.get('points')

        if room.current_story and points:
            room.current_story.final_points = points
            room.current_story.estimated_at = timezone.now()
            room.current_story.save()

        return Response(RoomSerializer(room).data)
