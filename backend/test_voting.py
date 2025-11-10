#!/usr/bin/env python3
"""
Test script to simulate 10 users voting in Planning Poker
"""
import json
import requests
from decimal import Decimal

# Room and story info
ROOM_CODE = "XO6ZEG"
BASE_URL = "http://localhost:8000"

def test_planning_poker_session():
    print("🎯 Testing Planning Poker with 10 Users")
    print("=" * 50)
    
    # Get room data
    room_response = requests.get(f"{BASE_URL}/api/rooms/{ROOM_CODE}/")
    room_data = room_response.json()
    
    participants = room_data['participants']
    current_story_id = room_data['current_story']
    current_story = room_data['current_story_data']
    
    print(f"📍 Room Code: {ROOM_CODE}")
    print(f"📖 Current Story: {current_story['story_id']} - {current_story['title']}")
    print(f"👥 Participants: {len(participants)} users")
    print()
    
    # Define voting pattern: User1=1, User2=2, User3=3, User4=5, User5=8, User6=13, User7=21, User8=1, User9=5, User10=8
    vote_values = ['1', '2', '3', '5', '8', '13', '21', '1', '5', '8']
    
    print("🗳️  Simulating Votes:")
    print("-" * 30)
    
    # Create votes directly in database by importing Django models
    import os
    import django
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
    django.setup()
    
    from rooms.models import Room, Participant, Vote, Story
    
    # Get Django objects
    room = Room.objects.get(code=ROOM_CODE)
    story = Story.objects.get(id=current_story_id)
    participants_db = Participant.objects.filter(room=room).order_by('joined_at')
    
    # Create votes
    total_votes = 0
    numeric_votes = []
    
    for i, participant in enumerate(participants_db):
        if i < len(vote_values):
            vote_value = vote_values[i]
            
            # Create or update vote
            vote, created = Vote.objects.update_or_create(
                participant=participant,
                story=story,
                defaults={'value': vote_value, 'room': room, 'revealed': False}
            )
            
            print(f"  {participant.username:<8} voted: {vote_value:>2}")
            
            # Calculate for average (exclude '?' and 'coffee')
            if vote_value not in ['?', 'coffee']:
                numeric_votes.append(int(vote_value))
            total_votes += 1
    
    print()
    
    # Calculate average
    if numeric_votes:
        average = sum(numeric_votes) / len(numeric_votes)
        rounded = round(average)
        
        print("📊 Voting Results:")
        print("-" * 20)
        print(f"  Total Votes: {total_votes}")
        print(f"  Numeric Votes: {numeric_votes}")
        print(f"  Sum: {sum(numeric_votes)}")
        print(f"  Average: {average:.2f}")
        print(f"  Rounded: {rounded}")
        print()
        
        # Reveal votes and set final points
        Vote.objects.filter(room=room, story=story).update(revealed=True)
        story.final_points = str(rounded)
        story.save()
        
        print(f"✅ Votes revealed and story points set to: {rounded}")
        
    # Check final room state
    room_response = requests.get(f"{BASE_URL}/api/rooms/{ROOM_CODE}/")
    final_room_data = room_response.json()
    
    print()
    print("📈 Final Room State:")
    print("-" * 25)
    
    # Calculate total points across all stories
    total_points = 0
    estimated_stories = 0
    
    for story in final_room_data['stories']:
        if story['final_points'] and story['final_points'] not in ['?', 'coffee']:
            points = int(story['final_points'])
            total_points += points
            estimated_stories += 1
            print(f"  📖 {story['story_id']}: {points} points")
    
    print()
    print(f"🏆 Total Points: {total_points} points across {estimated_stories} stories")
    
    return {
        'room_code': ROOM_CODE,
        'total_votes': total_votes,
        'average': average,
        'rounded': rounded,
        'total_points': total_points,
        'estimated_stories': estimated_stories
    }

if __name__ == "__main__":
    try:
        result = test_planning_poker_session()
        print()
        print("🎉 Test completed successfully!")
        print(f"   Room: {result['room_code']}")
        print(f"   Votes Cast: {result['total_votes']}")
        print(f"   Average: {result['average']:.2f} → {result['rounded']}")
        print(f"   Total Project Points: {result['total_points']}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()