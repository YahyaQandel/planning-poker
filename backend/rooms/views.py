import logging
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

# Set up logger for API operations
api_logger = logging.getLogger('rooms.api')
db_logger = logging.getLogger('rooms.database')


class RoomViewSet(viewsets.ModelViewSet):
    queryset = Room.objects.all()
    serializer_class = RoomSerializer
    lookup_field = 'code'

    def create(self, request):
        """Create a new room with optional initial story"""
        from .models import generate_funny_story
        
        serializer = CreateRoomSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        room = Room.objects.create()

        # Create initial story if provided, or generate a funny one
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
        else:
            # Generate a funny story as the initial story
            funny_id, funny_title = generate_funny_story()
            story = Story.objects.create(
                room=room,
                story_id=funny_id,
                title=funny_title,
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
        from .models import generate_funny_story
        
        room = get_object_or_404(Room, code=code)

        story_id = request.data.get('story_id', '')
        title = request.data.get('title', '')

        # Generate funny story if both ID and title are empty
        if not story_id and not title:
            story_id, title = generate_funny_story()
        # If only story_id is missing, generate a funny story_id
        elif not story_id:
            funny_id, _ = generate_funny_story()
            story_id = funny_id
        # If only title is missing, generate a funny title  
        elif not title:
            _, funny_title = generate_funny_story()
            title = funny_title

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
        """Reset room - clear all votes and estimation for current story"""
        room = get_object_or_404(Room, code=code)

        if room.current_story:
            # Delete all votes for current story
            Vote.objects.filter(room=room, story=room.current_story).delete()
            
            # Reset story estimation - clear final points and timestamp
            room.current_story.final_points = None
            room.current_story.estimated_at = None
            room.current_story.save()

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
                # Convert to integers and calculate estimate using Planning Poker best practices
                vote_values = [int(v) for v in numeric_votes]
                average = sum(vote_values) / len(vote_values)
                rounded = self.calculate_planning_poker_estimate(numeric_votes)

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

    @action(detail=True, methods=['post'])
    def clean_room(self, request, code=None):
        """Clean room - remove all disconnected participants and their votes"""
        api_logger.info(f"API CLEAN_ROOM - Request to clean room {code}")
        
        try:
            room = get_object_or_404(Room, code=code)
            api_logger.info(f"API CLEAN_ROOM - Found room {code} with {room.participants.count()} participants")
            
            # Find all disconnected participants
            disconnected_participants = room.participants.filter(connected=False)
            participant_count = disconnected_participants.count()
            
            if participant_count == 0:
                api_logger.info(f"API CLEAN_ROOM - No disconnected participants found in room {code}")
                return Response({
                    'message': 'No disconnected participants to remove',
                    'removed_count': 0,
                    'votes_removed': 0,
                    'removed_participants': [],
                    'room': RoomSerializer(room).data
                })

            # Log participant details before deletion
            participant_usernames = list(disconnected_participants.values_list('username', flat=True))
            api_logger.info(f"API CLEAN_ROOM - Found {participant_count} disconnected participants in room {code}: {participant_usernames}")
            
            # Delete votes associated with disconnected participants
            votes_deleted = 0
            for participant in disconnected_participants:
                participant_votes = participant.votes.count()
                db_logger.info(f"DB CLEAN - Removing {participant_votes} votes for disconnected participant {participant.username}")
                participant.votes.all().delete()
                votes_deleted += participant_votes
                db_logger.info(f"DB CLEAN - Removed {participant_votes} votes for disconnected participant {participant.username}")

            # Delete disconnected participants
            db_logger.info(f"DB CLEAN - Removing {participant_count} disconnected participants from room {code}")
            disconnected_participants.delete()
            
            result = {
                'message': f'Successfully removed {participant_count} disconnected participants',
                'removed_count': participant_count,
                'votes_removed': votes_deleted,
                'removed_participants': participant_usernames,
                'room': RoomSerializer(room).data
            }
            
            api_logger.info(f"API CLEAN_ROOM - Successfully cleaned room {code}: {result['message']}")
            db_logger.info(f"DB CLEAN - Successfully cleaned room {code}: removed {participant_count} participants, {votes_deleted} votes")
            
            return Response(result, status=status.HTTP_200_OK)
            
        except Exception as e:
            api_logger.error(f"API CLEAN_ROOM - Error cleaning room {code}: {str(e)}")
            db_logger.error(f"DB CLEAN - Error cleaning room {code}: {str(e)}")
            return Response(
                {'error': f'Failed to clean room: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def calculate_planning_poker_estimate(self, votes):
        """Calculate estimate using Planning Poker best practices"""
        fibonacci_sequence = [1, 2, 3, 5, 8, 13, 21, 34, 55, 89]
        
        if not votes:
            return None
            
        # Convert votes to integers and sort
        vote_values = sorted([int(v) for v in votes])
        min_vote = vote_values[0]
        max_vote = vote_values[-1]
        
        # Find positions in Fibonacci sequence
        min_pos = next((i for i, fib in enumerate(fibonacci_sequence) if fib >= min_vote), 0)
        max_pos = next((i for i, fib in enumerate(fibonacci_sequence) if fib >= max_vote), len(fibonacci_sequence) - 1)
        
        # Check for wide spread (more than 2 Fibonacci steps apart)
        spread = max_pos - min_pos
        
        if spread > 2:
            # Wide spread - suggest towards higher estimate with median approach
            # This encourages discussion and tends toward the complexity some see
            if len(vote_values) == 1:
                return vote_values[0]
            
            # Use 75th percentile approach for wide spreads
            import statistics
            percentile_75 = statistics.quantiles(vote_values, n=4)[2]  # 75th percentile
            
            # Round up to nearest Fibonacci
            for fib in fibonacci_sequence:
                if percentile_75 <= fib:
                    return fib
            return fibonacci_sequence[-1]
        else:
            # Normal spread - use median or standard approach
            import statistics
            median = statistics.median(vote_values)
            
            # Round to nearest Fibonacci (up)
            for fib in fibonacci_sequence:
                if median <= fib:
                    return fib
            return fibonacci_sequence[-1]
