import json
import logging
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.utils import timezone
from .models import Room, Participant, Vote, Story
from .serializers import RoomSerializer, ParticipantSerializer, VoteSerializer

# Set up loggers
websocket_logger = logging.getLogger('rooms.websocket')
db_logger = logging.getLogger('rooms.database')
redis_logger = logging.getLogger('rooms.redis')


class RoomConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_code = self.scope['url_route']['kwargs']['room_code']
        self.room_group_name = f'room_{self.room_code}'
        self.participant_id = None
        
        websocket_logger.info(f"WS CONNECT - New WebSocket connection to room {self.room_code}")
        websocket_logger.debug(f"WS CONNECT - Channel name: {self.channel_name}")

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        websocket_logger.info(f"WS CONNECT - Joined group {self.room_group_name}")

        await self.accept()
        websocket_logger.info(f"WS CONNECT - WebSocket connection accepted for room {self.room_code}")

    async def disconnect(self, close_code):
        websocket_logger.info(f"WS DISCONNECT - WebSocket disconnecting from room {self.room_code}, close_code: {close_code}")
        
        # Mark participant as disconnected if we have their ID
        if self.participant_id:
            websocket_logger.info(f"WS DISCONNECT - Marking participant {self.participant_id} as disconnected")
            await self.mark_user_disconnected(self.participant_id)
            room_data = await self.get_room_data()

            # Broadcast user disconnection to room
            websocket_logger.info(f"WS DISCONNECT - Broadcasting user_left for participant {self.participant_id}")
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'user_left_broadcast',
                    'participant_id': self.participant_id,
                    'room': room_data
                }
            )
        else:
            websocket_logger.info(f"WS DISCONNECT - No participant ID to disconnect")

        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
        websocket_logger.info(f"WS DISCONNECT - Left group {self.room_group_name}")

    async def receive(self, text_data):
        websocket_logger.info(f"WS RECEIVE - Message received in room {self.room_code}")
        websocket_logger.debug(f"WS RECEIVE - Raw message: {text_data}")
        
        try:
            data = json.loads(text_data)
            message_type = data.get('type')
            websocket_logger.info(f"WS RECEIVE - Message type: {message_type}")
            websocket_logger.debug(f"WS RECEIVE - Parsed data: {json.dumps(data, default=str)}")

            if message_type == 'vote':
                websocket_logger.info(f"WS RECEIVE - Handling vote message")
                await self.handle_vote(data)
            elif message_type == 'reveal':
                websocket_logger.info(f"WS RECEIVE - Handling reveal message")
                await self.handle_reveal(data)
            elif message_type == 'reset':
                websocket_logger.info(f"WS RECEIVE - Handling reset message")
                await self.handle_reset(data)
            elif message_type == 'confirm_points':
                websocket_logger.info(f"WS RECEIVE - Handling confirm_points message")
                await self.handle_confirm_points(data)
            elif message_type == 'add_story':
                websocket_logger.info(f"WS RECEIVE - Handling add_story message")
                await self.handle_add_story(data)
            elif message_type == 'change_story':
                websocket_logger.info(f"WS RECEIVE - Handling change_story message")
                await self.handle_change_story(data)
            elif message_type == 'switch_to_existing_story':
                websocket_logger.info(f"WS RECEIVE - Handling switch_to_existing_story message")
                await self.handle_switch_to_existing_story(data)
            elif message_type == 'user_joined':
                websocket_logger.info(f"WS RECEIVE - Handling user_joined message")
                await self.handle_user_joined(data)
            elif message_type == 'user_left':
                websocket_logger.info(f"WS RECEIVE - Handling user_left message")
                await self.handle_user_left(data)
            elif message_type == 'clean_room':
                websocket_logger.info(f"WS RECEIVE - Handling clean_room message")
                await self.handle_clean_room(data)
            else:
                websocket_logger.warning(f"WS RECEIVE - Unknown message type: {message_type}")
                
        except json.JSONDecodeError as e:
            websocket_logger.error(f"WS RECEIVE - Invalid JSON in message: {str(e)}")
        except Exception as e:
            websocket_logger.error(f"WS RECEIVE - Error handling message: {str(e)}")
            raise

    async def handle_vote(self, data):
        participant_id = data.get('participant_id')
        story_id = data.get('story_id')
        value = data.get('value')
        
        websocket_logger.info(f"WS VOTE - Participant {participant_id} voting '{value}' for story {story_id} in room {self.room_code}")
        websocket_logger.debug(f"WS VOTE - Vote data: {json.dumps(data, default=str)}")

        try:
            vote = await self.save_vote(participant_id, story_id, value)
            websocket_logger.info(f"WS VOTE - Vote saved successfully for participant {participant_id}")
            
            room_data = await self.get_room_data()

            # Broadcast vote to room
            websocket_logger.info(f"WS VOTE - Broadcasting vote_cast to room {self.room_code}")
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'vote_cast',
                    'participant_id': participant_id,
                    'has_voted': True,
                    'room': room_data
                }
            )
            websocket_logger.info(f"WS VOTE - Vote broadcast completed")
        except Exception as e:
            websocket_logger.error(f"WS VOTE - Error handling vote: {str(e)}")
            raise

    async def handle_reveal(self, data):
        websocket_logger.info(f"WS REVEAL - Revealing votes in room {self.room_code}")
        
        try:
            calculation_result = await self.reveal_votes()
            websocket_logger.info(f"WS REVEAL - Votes revealed, calculation result: {calculation_result}")
            
            room_data = await self.get_room_data()

            # Broadcast reveal to room with average calculation
            websocket_logger.info(f"WS REVEAL - Broadcasting votes_revealed to room {self.room_code}")
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'votes_revealed',
                    'room': room_data,
                    'average': calculation_result['average'] if calculation_result else None,
                    'rounded': calculation_result['rounded'] if calculation_result else None,
                    'discussion_message': calculation_result['discussion_message'] if calculation_result else None
                }
            )
            websocket_logger.info(f"WS REVEAL - Reveal broadcast completed")
        except Exception as e:
            websocket_logger.error(f"WS REVEAL - Error handling reveal: {str(e)}")
            raise

    async def handle_reset(self, data):
        await self.reset_votes()
        room_data = await self.get_room_data()

        # Broadcast reset to room
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'room_reset',
                'room': room_data
            }
        )

    async def handle_confirm_points(self, data):
        points = data.get('points')
        await self.confirm_story_points(points)
        room_data = await self.get_room_data()

        # Broadcast confirmation to room
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'points_confirmed',
                'room': room_data
            }
        )

    async def handle_add_story(self, data):
        story_id = data.get('story_id', '')
        title = data.get('title', '')
        
        websocket_logger.info(f"WS ADD_STORY - Adding story '{story_id}': '{title}' to room {self.room_code}")
        websocket_logger.debug(f"WS ADD_STORY - Story data: {json.dumps(data, default=str)}")

        try:
            result = await self.add_story(story_id, title)
            websocket_logger.info(f"WS ADD_STORY - Story creation result: exists={result.get('exists')}")
            
            room_data = await self.get_room_data()

            # If story already exists, ask for confirmation
            if result.get('exists'):
                websocket_logger.info(f"WS ADD_STORY - Story already exists, sending confirmation request")
                await self.send(text_data=json.dumps({
                    'type': 'story_exists',
                    'story': result['story'],
                    'room': room_data
                }))
            else:
                # Broadcast new story to room
                websocket_logger.info(f"WS ADD_STORY - Broadcasting story_added to room {self.room_code}")
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'story_added',
                        'story': result['story'],
                        'room': room_data
                    }
                )
                websocket_logger.info(f"WS ADD_STORY - Story broadcast completed")
        except Exception as e:
            websocket_logger.error(f"WS ADD_STORY - Error adding story: {str(e)}")
            raise

    async def handle_change_story(self, data):
        story_id = data.get('story_id')

        await self.change_current_story(story_id)
        room_data = await self.get_room_data()

        # Broadcast story change to room
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'story_changed',
                'room': room_data
            }
        )

    async def handle_switch_to_existing_story(self, data):
        story_id = data.get('story_id')

        await self.switch_to_existing_story(story_id)
        room_data = await self.get_room_data()

        # Broadcast story change to room
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'story_changed',
                'room': room_data
            }
        )

    async def handle_user_joined(self, data):
        username = data.get('username')
        participant_id = data.get('participant_id')
        
        # Store participant ID for disconnection handling
        if participant_id:
            self.participant_id = participant_id
            # Ensure participant is marked as connected
            await self.mark_user_connected(participant_id)
        elif username:
            # Fallback: find participant by username if ID not provided
            participant = await self.get_participant_by_username(username)
            if participant:
                self.participant_id = participant['id']
                await self.mark_user_connected(self.participant_id)

        room_data = await self.get_room_data()

        # Broadcast user joined to room
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'user_joined_broadcast',
                'username': username,
                'room': room_data
            }
        )

    async def handle_user_left(self, data):
        participant_id = data.get('participant_id')

        await self.mark_user_disconnected(participant_id)
        room_data = await self.get_room_data()

        # Broadcast user left to room
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'user_left_broadcast',
                'participant_id': participant_id,
                'room': room_data
            }
        )

    async def handle_clean_room(self, data):
        """Handle cleaning all disconnected participants from the room"""
        websocket_logger.info(f"WS CLEAN_ROOM - Request to clean room {self.room_code}")
        
        try:
            result = await self.clean_disconnected_participants()
            room_data = await self.get_room_data()
            
            websocket_logger.info(f"WS CLEAN_ROOM - Successfully cleaned room {self.room_code}: {result}")

            # Broadcast clean room result to all participants
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'room_cleaned',
                    'removed_count': result['removed_count'],
                    'votes_removed': result['votes_removed'],
                    'removed_participants': result['removed_participants'],
                    'room': room_data
                }
            )
            
        except Exception as e:
            websocket_logger.error(f"WS CLEAN_ROOM - Error cleaning room {self.room_code}: {str(e)}")
            # Send error only to the requesting client
            await self.send(text_data=json.dumps({
                'type': 'clean_room_error',
                'error': str(e)
            }))

    # Broadcast handlers
    async def vote_cast(self, event):
        await self.send(text_data=json.dumps({
            'type': 'vote_cast',
            'participant_id': event['participant_id'],
            'has_voted': event['has_voted'],
            'room': event['room']
        }))

    async def votes_revealed(self, event):
        await self.send(text_data=json.dumps({
            'type': 'votes_revealed',
            'room': event['room'],
            'average': event.get('average'),
            'rounded': event.get('rounded'),
            'discussion_message': event.get('discussion_message')
        }))

    async def points_confirmed(self, event):
        await self.send(text_data=json.dumps({
            'type': 'points_confirmed',
            'room': event['room']
        }))

    async def room_reset(self, event):
        await self.send(text_data=json.dumps({
            'type': 'room_reset',
            'room': event['room']
        }))

    async def story_added(self, event):
        await self.send(text_data=json.dumps({
            'type': 'story_added',
            'story': event['story'],
            'room': event['room']
        }))

    async def story_changed(self, event):
        await self.send(text_data=json.dumps({
            'type': 'story_changed',
            'room': event['room']
        }))

    async def user_joined_broadcast(self, event):
        await self.send(text_data=json.dumps({
            'type': 'user_joined',
            'username': event['username'],
            'room': event['room']
        }))

    async def user_left_broadcast(self, event):
        await self.send(text_data=json.dumps({
            'type': 'user_left',
            'participant_id': event['participant_id'],
            'room': event['room']
        }))

    async def room_cleaned(self, event):
        """Broadcast room cleaned event to all participants"""
        await self.send(text_data=json.dumps({
            'type': 'room_cleaned',
            'removed_count': event['removed_count'],
            'votes_removed': event['votes_removed'],
            'removed_participants': event['removed_participants'],
            'room': event['room']
        }))

    # Database operations
    @database_sync_to_async
    def save_vote(self, participant_id, story_id, value):
        from .models import Participant, Story, Vote, Room

        room = Room.objects.get(code=self.room_code)
        participant = Participant.objects.get(id=participant_id)
        story = Story.objects.get(id=story_id)

        vote, created = Vote.objects.update_or_create(
            participant=participant,
            story=story,
            defaults={'value': value, 'room': room}
        )

        return VoteSerializer(vote).data

    @database_sync_to_async
    def reveal_votes(self):
        from .models import Room, Vote

        room = Room.objects.get(code=self.room_code)

        if room.current_story:
            votes = Vote.objects.filter(room=room, story=room.current_story)
            votes.update(revealed=True)

            # Calculate estimate using Planning Poker best practices (excluding ? and coffee)
            numeric_votes = votes.exclude(value__in=['?', 'coffee']).values_list('value', flat=True)
            if numeric_votes:
                vote_values = [int(v) for v in numeric_votes]
                average = sum(vote_values) / len(vote_values)  # Keep for display
                rounded = self.calculate_planning_poker_estimate(numeric_votes)

                # Check for discussion suggestion
                discussion_message = self.get_discussion_suggestion(votes, numeric_votes)
                
                # Don't save yet - wait for confirmation
                # Just mark as revealed
                return {
                    'average': average, 
                    'rounded': rounded,
                    'discussion_message': discussion_message
                }
        return None

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

    def get_discussion_suggestion(self, all_votes, numeric_votes):
        """Generate discussion suggestion when there are wide spreads in votes"""
        if not numeric_votes or len(numeric_votes) < 2:
            return None
            
        # Convert to integers and find min/max
        vote_values = [int(v) for v in numeric_votes]
        min_vote = min(vote_values)
        max_vote = max(vote_values)
        
        # Find Fibonacci positions
        fibonacci_sequence = [1, 2, 3, 5, 8, 13, 21, 34, 55, 89]
        min_pos = next((i for i, fib in enumerate(fibonacci_sequence) if fib >= min_vote), 0)
        max_pos = next((i for i, fib in enumerate(fibonacci_sequence) if fib >= max_vote), len(fibonacci_sequence) - 1)
        
        # Check for wide spread (more than 2 Fibonacci steps apart)
        spread = max_pos - min_pos
        
        if spread > 2:
            # Find participants with min and max votes
            min_voters = []
            max_voters = []
            
            for vote in all_votes:
                if vote.value not in ['?', 'coffee']:
                    vote_val = int(vote.value)
                    if vote_val == min_vote:
                        min_voters.append(vote.participant.username)
                    elif vote_val == max_vote:
                        max_voters.append(vote.participant.username)
            
            # Create discussion message
            min_voter = min_voters[0] if min_voters else "someone"
            max_voter = max_voters[0] if max_voters else "someone"
            
            return {
                "message": f"Wide spread detected! {min_voter} (voted {min_vote}) and {max_voter} (voted {max_vote}) should discuss the story complexity.",
                "min_vote": min_vote,
                "max_vote": max_vote,
                "min_voter": min_voter,
                "max_voter": max_voter,
                "spread_level": "high" if spread > 4 else "medium"
            }
        
        return None

    @database_sync_to_async
    def reset_votes(self):
        from .models import Room, Vote

        room = Room.objects.get(code=self.room_code)

        if room.current_story:
            # Delete all votes for current story
            Vote.objects.filter(room=room, story=room.current_story).delete()
            
            # Reset story estimation - clear final points and timestamp
            room.current_story.final_points = None
            room.current_story.estimated_at = None
            room.current_story.save()

    @database_sync_to_async
    def confirm_story_points(self, points):
        from .models import Room

        room = Room.objects.get(code=self.room_code)

        if room.current_story:
            room.current_story.final_points = str(points)
            room.current_story.estimated_at = timezone.now()
            room.current_story.save()

    @database_sync_to_async
    def add_story(self, story_id, title):
        from .models import Room, Story, Vote, generate_funny_story

        room = Room.objects.get(code=self.room_code)

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

        # Check if story with same story_id already exists (if story_id is provided)
        if story_id:
            existing_story = Story.objects.filter(room=room, story_id=story_id).first()
            if existing_story:
                # Return existing story info with a flag
                from .serializers import StorySerializer
                return {
                    'story': StorySerializer(existing_story).data,
                    'exists': True
                }

        max_order = Story.objects.filter(room=room).count()

        story = Story.objects.create(
            room=room,
            story_id=story_id,
            title=title,
            order=max_order
        )

        # Always set as current story and clear votes for previous story
        if room.current_story:
            # Clear votes for previous story
            Vote.objects.filter(room=room, story=room.current_story).delete()

        room.current_story = story
        room.save()

        from .serializers import StorySerializer
        return {
            'story': StorySerializer(story).data,
            'exists': False
        }

    @database_sync_to_async
    def change_current_story(self, story_id):
        from .models import Room, Story, Vote

        room = Room.objects.get(code=self.room_code)
        story = Story.objects.get(id=story_id)

        # Don't delete votes when switching stories - preserve them!
        # Only switch the current story pointer
        room.current_story = story
        room.save()

    @database_sync_to_async
    def switch_to_existing_story(self, story_id):
        from .models import Room, Story, Vote

        room = Room.objects.get(code=self.room_code)
        story = Story.objects.get(id=story_id)

        # Don't delete votes when switching stories - preserve them!
        # Only switch the current story pointer
        room.current_story = story
        room.save()

    @database_sync_to_async
    def mark_user_disconnected(self, participant_id):
        from .models import Participant

        try:
            participant = Participant.objects.get(id=participant_id)
            participant.connected = False
            participant.save()
        except Participant.DoesNotExist:
            pass

    @database_sync_to_async
    def mark_user_connected(self, participant_id):
        from .models import Participant

        try:
            participant = Participant.objects.get(id=participant_id)
            participant.connected = True
            participant.save()
        except Participant.DoesNotExist:
            pass

    @database_sync_to_async
    def get_participant_by_username(self, username):
        from .models import Participant, Room
        from .serializers import ParticipantSerializer

        try:
            room = Room.objects.get(code=self.room_code)
            participant = Participant.objects.get(room=room, username=username)
            return ParticipantSerializer(participant).data
        except Participant.DoesNotExist:
            return None

    @database_sync_to_async
    def get_room_data(self):
        from .models import Room
        import json

        room = Room.objects.get(code=self.room_code)
        # Convert to JSON and back to ensure all UUIDs are converted to strings
        serialized_data = RoomSerializer(room).data
        return json.loads(json.dumps(serialized_data, default=str))

    @database_sync_to_async
    def clean_disconnected_participants(self):
        """Clean all disconnected participants from the room"""
        from .models import Room, Participant, Vote
        
        db_logger.info(f"DB CLEAN - Starting clean operation for room {self.room_code}")
        
        room = Room.objects.get(code=self.room_code)
        
        # Find all disconnected participants
        disconnected_participants = Participant.objects.filter(room=room, connected=False)
        participant_count = disconnected_participants.count()
        
        if participant_count == 0:
            db_logger.info(f"DB CLEAN - No disconnected participants found in room {self.room_code}")
            return {
                'removed_count': 0,
                'votes_removed': 0,
                'removed_participants': []
            }

        # Log participant details before deletion
        participant_usernames = list(disconnected_participants.values_list('username', flat=True))
        db_logger.info(f"DB CLEAN - Found {participant_count} disconnected participants in room {self.room_code}: {participant_usernames}")
        
        # Delete votes associated with disconnected participants
        votes_deleted = 0
        for participant in disconnected_participants:
            participant_votes = Vote.objects.filter(participant=participant).count()
            Vote.objects.filter(participant=participant).delete()
            votes_deleted += participant_votes
            db_logger.info(f"DB CLEAN - Removed {participant_votes} votes for disconnected participant {participant.username}")

        # Delete disconnected participants
        db_logger.info(f"DB CLEAN - Removing {participant_count} disconnected participants from room {self.room_code}")
        disconnected_participants.delete()
        
        result = {
            'removed_count': participant_count,
            'votes_removed': votes_deleted,
            'removed_participants': participant_usernames
        }
        
        db_logger.info(f"DB CLEAN - Successfully cleaned room {self.room_code}: {result}")
        return result
