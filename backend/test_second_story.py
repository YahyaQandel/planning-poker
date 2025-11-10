#!/usr/bin/env python3
"""
Test script for second story voting
"""
import json
import requests
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from rooms.models import Room, Participant, Vote, Story

ROOM_CODE = "XO6ZEG"
BASE_URL = "http://localhost:8000"

def test_second_story():
    print("🎯 Testing Second Story: TEST-123 - User Authentication Module")
    print("=" * 60)
    
    # Get room and find the new story
    room = Room.objects.get(code=ROOM_CODE)
    story = Story.objects.filter(room=room, story_id="TEST-123").first()
    
    if not story:
        print("❌ Story TEST-123 not found!")
        return
    
    # Set as current story
    room.current_story = story
    room.save()
    
    participants = Participant.objects.filter(room=room).order_by('joined_at')
    
    print(f"📖 Story: {story.story_id} - {story.title}")
    print(f"👥 Participants: {participants.count()} users")
    print()
    
    # Different voting pattern for second story: mostly higher values
    vote_values = ['5', '8', '8', '13', '13', '21', '13', '8', '5', '8']
    
    print("🗳️  Voting on Second Story:")
    print("-" * 35)
    
    numeric_votes = []
    
    for i, participant in enumerate(participants):
        if i < len(vote_values):
            vote_value = vote_values[i]
            
            # Create vote for new story
            vote, created = Vote.objects.update_or_create(
                participant=participant,
                story=story,
                defaults={'value': vote_value, 'room': room, 'revealed': False}
            )
            
            print(f"  {participant.username:<8} voted: {vote_value:>2}")
            
            if vote_value not in ['?', 'coffee']:
                numeric_votes.append(int(vote_value))
    
    # Calculate and set results
    average = sum(numeric_votes) / len(numeric_votes)
    rounded = round(average)
    
    print()
    print("📊 Second Story Results:")
    print("-" * 25)
    print(f"  Votes: {numeric_votes}")
    print(f"  Sum: {sum(numeric_votes)}")
    print(f"  Average: {average:.2f}")
    print(f"  Rounded: {rounded}")
    
    # Reveal and finalize
    Vote.objects.filter(room=room, story=story).update(revealed=True)
    story.final_points = str(rounded)
    story.save()
    
    print(f"✅ Second story completed with {rounded} points!")
    print()
    
    # Show final project totals
    all_stories = Story.objects.filter(room=room)
    total_points = 0
    estimated_count = 0
    
    print("📊 Complete Project Summary:")
    print("-" * 30)
    
    for s in all_stories:
        if s.final_points and s.final_points not in ['?', 'coffee']:
            points = int(s.final_points)
            total_points += points
            estimated_count += 1
            print(f"  📖 {s.story_id}: {points:>2} points - {s.title}")
    
    print()
    print(f"🏆 TOTAL PROJECT: {total_points} points across {estimated_count} stories")
    
    return {
        'total_points': total_points,
        'story_count': estimated_count,
        'second_story_points': rounded
    }

if __name__ == "__main__":
    try:
        result = test_second_story()
        print()
        print("🎉 Complete multi-story test successful!")
        print(f"   Second story points: {result['second_story_points']}")
        print(f"   Total project points: {result['total_points']}")
        print(f"   Stories completed: {result['story_count']}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()