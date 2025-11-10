import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.utils import timezone
from .models import Room, Participant, Vote, Story
from .serializers import RoomSerializer, ParticipantSerializer, VoteSerializer


class RoomConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_code = self.scope['url_route']['kwargs']['room_code']
        self.room_group_name = f'room_{self.room_code}'

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        message_type = data.get('type')

        if message_type == 'vote':
            await self.handle_vote(data)
        elif message_type == 'reveal':
            await self.handle_reveal(data)
        elif message_type == 'reset':
            await self.handle_reset(data)
        elif message_type == 'confirm_points':
            await self.handle_confirm_points(data)
        elif message_type == 'add_story':
            await self.handle_add_story(data)
        elif message_type == 'change_story':
            await self.handle_change_story(data)
        elif message_type == 'switch_to_existing_story':
            await self.handle_switch_to_existing_story(data)
        elif message_type == 'user_joined':
            await self.handle_user_joined(data)
        elif message_type == 'user_left':
            await self.handle_user_left(data)

    async def handle_vote(self, data):
        participant_id = data.get('participant_id')
        story_id = data.get('story_id')
        value = data.get('value')

        vote = await self.save_vote(participant_id, story_id, value)
        room_data = await self.get_room_data()

        # Broadcast vote to room
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'vote_cast',
                'participant_id': participant_id,
                'has_voted': True,
                'room': room_data
            }
        )

    async def handle_reveal(self, data):
        calculation_result = await self.reveal_votes()
        room_data = await self.get_room_data()

        # Broadcast reveal to room with average calculation
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'votes_revealed',
                'room': room_data,
                'average': calculation_result['average'] if calculation_result else None,
                'rounded': calculation_result['rounded'] if calculation_result else None
            }
        )

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

        result = await self.add_story(story_id, title)
        room_data = await self.get_room_data()

        # If story already exists, ask for confirmation
        if result.get('exists'):
            await self.send(text_data=json.dumps({
                'type': 'story_exists',
                'story': result['story'],
                'room': room_data
            }))
        else:
            # Broadcast new story to room
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'story_added',
                    'story': result['story'],
                    'room': room_data
                }
            )

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
            'rounded': event.get('rounded')
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

            # Calculate average (excluding ? and coffee)
            numeric_votes = votes.exclude(value__in=['?', 'coffee']).values_list('value', flat=True)
            if numeric_votes:
                vote_values = [int(v) for v in numeric_votes]
                average = sum(vote_values) / len(vote_values)
                rounded = round(average)

                # Don't save yet - wait for confirmation
                # Just mark as revealed
                return {'average': average, 'rounded': rounded}
        return None

    @database_sync_to_async
    def reset_votes(self):
        from .models import Room, Vote

        room = Room.objects.get(code=self.room_code)

        if room.current_story:
            Vote.objects.filter(room=room, story=room.current_story).delete()

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
        from .models import Room, Story, Vote

        room = Room.objects.get(code=self.room_code)

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
        from .models import Room, Story

        room = Room.objects.get(code=self.room_code)
        story = Story.objects.get(id=story_id)

        room.current_story = story
        room.save()

    @database_sync_to_async
    def switch_to_existing_story(self, story_id):
        from .models import Room, Story, Vote

        room = Room.objects.get(code=self.room_code)
        story = Story.objects.get(id=story_id)

        # Clear votes for previous story if different
        if room.current_story and room.current_story.id != story.id:
            Vote.objects.filter(room=room, story=room.current_story).delete()

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
    def get_room_data(self):
        from .models import Room
        import json

        room = Room.objects.get(code=self.room_code)
        # Convert to JSON and back to ensure all UUIDs are converted to strings
        serialized_data = RoomSerializer(room).data
        return json.loads(json.dumps(serialized_data, default=str))
