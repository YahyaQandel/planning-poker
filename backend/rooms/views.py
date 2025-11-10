from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.utils import timezone
import logging
import json
from .models import Room, Participant, Story, Vote
from .serializers import (
    RoomSerializer,
    ParticipantSerializer,
    StorySerializer,
    VoteSerializer,
    CreateRoomSerializer,
    JoinRoomSerializer
)

# Set up loggers
api_logger = logging.getLogger('rooms.api')
db_logger = logging.getLogger('rooms.database')


class RoomViewSet(viewsets.ModelViewSet):
    queryset = Room.objects.all()
    serializer_class = RoomSerializer
    lookup_field = 'code'

    def create(self, request):
        """Create a new room with optional initial story"""
        api_logger.info(f"API CREATE ROOM - Request received from IP: {request.META.get('REMOTE_ADDR')}")
        api_logger.debug(f"API CREATE ROOM - Request data: {json.dumps(request.data, default=str)}")
        
        from .models import generate_funny_story
        
        try:
            serializer = CreateRoomSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            api_logger.debug(f"API CREATE ROOM - Serializer validation passed: {serializer.validated_data}")

            # Database operation: Create room
            db_logger.info("DB CREATE - Creating new Room object")
            room = Room.objects.create()
            db_logger.info(f"DB CREATE - Room created with code: {room.code}")

            # Create initial story if provided, or generate a funny one
            story_id = serializer.validated_data.get('story_id')
            title = serializer.validated_data.get('title')
            api_logger.debug(f"API CREATE ROOM - Story data: story_id='{story_id}', title='{title}'")

            if story_id or title:
                db_logger.info(f"DB CREATE - Creating story with provided data: {story_id}, {title}")
                story = Story.objects.create(
                    room=room,
                    story_id=story_id or '',
                    title=title or '',
                    order=0
                )
                db_logger.info(f"DB CREATE - Story created with ID: {story.id}")
                room.current_story = story
                db_logger.info(f"DB UPDATE - Room {room.code} current_story set to {story.id}")
                room.save()
            else:
                # Generate a funny story as the initial story
                funny_id, funny_title = generate_funny_story()
                api_logger.debug(f"API CREATE ROOM - Generated funny story: {funny_id}, {funny_title}")
                db_logger.info(f"DB CREATE - Creating funny story: {funny_id}, {funny_title}")
                story = Story.objects.create(
                    room=room,
                    story_id=funny_id,
                    title=funny_title,
                    order=0
                )
                db_logger.info(f"DB CREATE - Funny story created with ID: {story.id}")
                room.current_story = story
                db_logger.info(f"DB UPDATE - Room {room.code} current_story set to {story.id}")
                room.save()

            response_data = RoomSerializer(room).data
            api_logger.info(f"API CREATE ROOM - Success: Room {room.code} created with story {story.id}")
            api_logger.debug(f"API CREATE ROOM - Response data: {json.dumps(response_data, default=str)}")
            return Response(response_data, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            api_logger.error(f"API CREATE ROOM - Error: {str(e)}")
            raise

    def retrieve(self, request, code=None):
        """Get room details"""
        api_logger.info(f"API GET ROOM - Request for room {code} from IP: {request.META.get('REMOTE_ADDR')}")
        
        try:
            db_logger.info(f"DB READ - Fetching room with code: {code}")
            room = get_object_or_404(Room, code=code)
            db_logger.info(f"DB READ - Room {code} found with {room.participants.count()} participants")
            
            response_data = RoomSerializer(room).data
            api_logger.info(f"API GET ROOM - Success: Room {code} data retrieved")
            api_logger.debug(f"API GET ROOM - Response data: {json.dumps(response_data, default=str)}")
            return Response(response_data)
            
        except Exception as e:
            api_logger.error(f"API GET ROOM - Error retrieving room {code}: {str(e)}")
            raise

    @action(detail=True, methods=['post'])
    def join(self, request, code=None):
        """Join a room"""
        api_logger.info(f"API JOIN ROOM - Request to join room {code} from IP: {request.META.get('REMOTE_ADDR')}")
        api_logger.debug(f"API JOIN ROOM - Request data: {json.dumps(request.data, default=str)}")
        
        try:
            db_logger.info(f"DB READ - Fetching room with code: {code}")
            room = get_object_or_404(Room, code=code)
            
            serializer = JoinRoomSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            api_logger.debug(f"API JOIN ROOM - Serializer validation passed: {serializer.validated_data}")

            username = serializer.validated_data['username']
            session_id = serializer.validated_data['session_id']
            api_logger.info(f"API JOIN ROOM - User '{username}' attempting to join room {code}")

            # Check if participant already exists
            db_logger.info(f"DB READ/CREATE - Checking if participant '{username}' exists in room {code}")
            participant, created = Participant.objects.get_or_create(
                room=room,
                username=username,
                defaults={'session_id': session_id, 'connected': True}
            )

            if created:
                db_logger.info(f"DB CREATE - New participant created: {username} in room {code}")
                api_logger.info(f"API JOIN ROOM - New participant '{username}' created and joined room {code}")
            else:
                db_logger.info(f"DB UPDATE - Existing participant '{username}' reconnecting to room {code}")
                participant.session_id = session_id
                participant.connected = True
                participant.save()
                api_logger.info(f"API JOIN ROOM - Existing participant '{username}' reconnected to room {code}")

            response_data = {
                'participant': ParticipantSerializer(participant).data,
                'room': RoomSerializer(room).data
            }
            api_logger.info(f"API JOIN ROOM - Success: User '{username}' joined room {code}")
            api_logger.debug(f"API JOIN ROOM - Response data: {json.dumps(response_data, default=str)}")
            return Response(response_data)
            
        except Exception as e:
            api_logger.error(f"API JOIN ROOM - Error joining room {code}: {str(e)}")
            raise

    @action(detail=True, methods=['post'])
    def add_story(self, request, code=None):
        """Add a new story to estimate"""
        api_logger.info(f"API ADD STORY - Request to add story to room {code} from IP: {request.META.get('REMOTE_ADDR')}")
        api_logger.debug(f"API ADD STORY - Request data: {json.dumps(request.data, default=str)}")
        
        from .models import generate_funny_story
        
        try:
            db_logger.info(f"DB READ - Fetching room with code: {code}")
            room = get_object_or_404(Room, code=code)

            story_id = request.data.get('story_id', '')
            title = request.data.get('title', '')
            api_logger.debug(f"API ADD STORY - Original story data: story_id='{story_id}', title='{title}'")

            # Generate funny story if both ID and title are empty
            if not story_id and not title:
                story_id, title = generate_funny_story()
                api_logger.debug(f"API ADD STORY - Generated funny story (both empty): {story_id}, {title}")
            # If only story_id is missing, generate a funny story_id
            elif not story_id:
                funny_id, _ = generate_funny_story()
                story_id = funny_id
                api_logger.debug(f"API ADD STORY - Generated funny ID: {story_id}")
            # If only title is missing, generate a funny title  
            elif not title:
                _, funny_title = generate_funny_story()
                title = funny_title
                api_logger.debug(f"API ADD STORY - Generated funny title: {title}")

            # Get the highest order number
            db_logger.info(f"DB READ - Getting story count for room {code}")
            max_order = Story.objects.filter(room=room).count()
            api_logger.debug(f"API ADD STORY - New story order will be: {max_order}")

            db_logger.info(f"DB CREATE - Creating story: {story_id}, {title} in room {code}")
            story = Story.objects.create(
                room=room,
                story_id=story_id,
                title=title,
                order=max_order
            )
            db_logger.info(f"DB CREATE - Story created with ID: {story.id}")

            # Set as current story if no current story
            if not room.current_story:
                db_logger.info(f"DB UPDATE - Setting new story as current story for room {code}")
                room.current_story = story
                room.save()
                api_logger.info(f"API ADD STORY - New story set as current story")

            response_data = StorySerializer(story).data
            api_logger.info(f"API ADD STORY - Success: Story '{story_id}' added to room {code}")
            api_logger.debug(f"API ADD STORY - Response data: {json.dumps(response_data, default=str)}")
            return Response(response_data, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            api_logger.error(f"API ADD STORY - Error adding story to room {code}: {str(e)}")
            raise

    @action(detail=True, methods=['post'])
    def reset(self, request, code=None):
        """Reset room - clear all votes and estimation for current story"""
        api_logger.info(f"API RESET ROOM - Request to reset room {code} from IP: {request.META.get('REMOTE_ADDR')}")
        
        try:
            db_logger.info(f"DB READ - Fetching room with code: {code}")
            room = get_object_or_404(Room, code=code)

            if room.current_story:
                story_id = room.current_story.id
                api_logger.info(f"API RESET ROOM - Resetting current story {story_id} in room {code}")
                
                # Delete all votes for current story
                db_logger.info(f"DB DELETE - Removing all votes for story {story_id} in room {code}")
                vote_count = Vote.objects.filter(room=room, story=room.current_story).count()
                Vote.objects.filter(room=room, story=room.current_story).delete()
                db_logger.info(f"DB DELETE - {vote_count} votes deleted for story {story_id}")
                
                # Reset story estimation - clear final points and timestamp
                db_logger.info(f"DB UPDATE - Clearing estimation data for story {story_id}")
                room.current_story.final_points = None
                room.current_story.estimated_at = None
                room.current_story.save()
                api_logger.info(f"API RESET ROOM - Story {story_id} estimation data cleared")
            else:
                api_logger.info(f"API RESET ROOM - No current story in room {code} to reset")

            api_logger.info(f"API RESET ROOM - Success: Room {code} reset completed")
            return Response({'message': 'Room reset successfully'})
            
        except Exception as e:
            api_logger.error(f"API RESET ROOM - Error resetting room {code}: {str(e)}")
            raise

    @action(detail=True, methods=['post'])
    def reveal(self, request, code=None):
        """Reveal all votes for current story"""
        api_logger.info(f"API REVEAL VOTES - Request to reveal votes in room {code} from IP: {request.META.get('REMOTE_ADDR')}")
        
        try:
            db_logger.info(f"DB READ - Fetching room with code: {code}")
            room = get_object_or_404(Room, code=code)

            if room.current_story:
                story_id = room.current_story.id
                api_logger.info(f"API REVEAL VOTES - Revealing votes for story {story_id} in room {code}")
                
                db_logger.info(f"DB READ - Fetching votes for story {story_id}")
                votes = Vote.objects.filter(room=room, story=room.current_story)
                vote_count = votes.count()
                api_logger.debug(f"API REVEAL VOTES - Found {vote_count} votes to reveal")
                
                db_logger.info(f"DB UPDATE - Setting revealed=True for {vote_count} votes")
                votes.update(revealed=True)

                # Calculate average (excluding ? and coffee)
                numeric_votes = votes.exclude(value__in=['?', 'coffee']).values_list('value', flat=True)
                if numeric_votes:
                    api_logger.debug(f"API REVEAL VOTES - Numeric votes: {list(numeric_votes)}")
                    # Convert to integers and calculate estimate using Planning Poker best practices
                    vote_values = [int(v) for v in numeric_votes]
                    average = sum(vote_values) / len(vote_values)
                    rounded = self.calculate_planning_poker_estimate(numeric_votes)
                    api_logger.info(f"API REVEAL VOTES - Calculated average: {average:.2f}, recommended: {rounded}")

                    # Store both average and rounded value (we'll use rounded as placeholder)
                    db_logger.info(f"DB UPDATE - Setting final_points={rounded} for story {story_id}")
                    room.current_story.final_points = str(rounded)
                    room.current_story.estimated_at = timezone.now()
                    room.current_story.save()
                    api_logger.info(f"API REVEAL VOTES - Story {story_id} estimation saved: {rounded} points")
                else:
                    api_logger.info(f"API REVEAL VOTES - No numeric votes found for story {story_id}")
            else:
                api_logger.info(f"API REVEAL VOTES - No current story in room {code} to reveal")

            response_data = RoomSerializer(room).data
            api_logger.info(f"API REVEAL VOTES - Success: Votes revealed for room {code}")
            api_logger.debug(f"API REVEAL VOTES - Response data: {json.dumps(response_data, default=str)}")
            return Response(response_data)
            
        except Exception as e:
            api_logger.error(f"API REVEAL VOTES - Error revealing votes in room {code}: {str(e)}")
            raise

    @action(detail=True, methods=['post'])
    def confirm_points(self, request, code=None):
        """Confirm and finalize story points"""
        api_logger.info(f"API CONFIRM POINTS - Request to confirm points in room {code} from IP: {request.META.get('REMOTE_ADDR')}")
        api_logger.debug(f"API CONFIRM POINTS - Request data: {json.dumps(request.data, default=str)}")
        
        try:
            db_logger.info(f"DB READ - Fetching room with code: {code}")
            room = get_object_or_404(Room, code=code)
            points = request.data.get('points')
            api_logger.info(f"API CONFIRM POINTS - Confirming {points} points for current story in room {code}")

            if room.current_story and points:
                story_id = room.current_story.id
                db_logger.info(f"DB UPDATE - Setting final_points={points} for story {story_id}")
                room.current_story.final_points = points
                room.current_story.estimated_at = timezone.now()
                room.current_story.save()
                api_logger.info(f"API CONFIRM POINTS - Story {story_id} points confirmed: {points}")
            else:
                if not room.current_story:
                    api_logger.warning(f"API CONFIRM POINTS - No current story in room {code}")
                if not points:
                    api_logger.warning(f"API CONFIRM POINTS - No points provided in request")

            response_data = RoomSerializer(room).data
            api_logger.info(f"API CONFIRM POINTS - Success: Points confirmed for room {code}")
            api_logger.debug(f"API CONFIRM POINTS - Response data: {json.dumps(response_data, default=str)}")
            return Response(response_data)
            
        except Exception as e:
            api_logger.error(f"API CONFIRM POINTS - Error confirming points in room {code}: {str(e)}")
            raise

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
