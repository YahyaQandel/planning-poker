#!/usr/bin/env python3
"""
Add votes to WOW-316 and TEST-123 stories for testing
"""
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

import requests
from rooms.models import Room, Participant, Vote, Story

def add_votes_to_stories():
    room_code = "XO6ZEG"
    base_url = "http://localhost:8000"
    
    print("🎯 Adding votes to WOW-316 and TEST-123 stories")
    print("=" * 55)
    
    # Get room and participants
    room = Room.objects.get(code=room_code)
    participants = list(Participant.objects.filter(room=room).order_by('joined_at')[:10])
    
    print(f"📍 Room: {room_code}")
    print(f"👥 Participants: {len(participants)} users")
    print()
    
    # Get stories
    wow_story = Story.objects.filter(room=room, story_id="WOW-316").first()
    test_story = Story.objects.filter(room=room, story_id="TEST-123").first()
    
    if not wow_story:
        print("❌ WOW-316 story not found!")
        return
        
    if not test_story:
        print("❌ TEST-123 story not found!")
        return
    
    # Vote patterns
    wow_votes = ['2', '3', '5', '8', '5', '8', '13', '3', '5', '8']  # Average: 6.0 → 6 points
    test_votes = ['8', '13', '13', '21', '13', '13', '21', '8', '13', '13']  # Average: 13.6 → 14 points
    
    print("🗳️  Adding votes to WOW-316:")
    print("-" * 30)
    
    # Add votes to WOW-316
    total_wow = 0
    for i, participant in enumerate(participants):
        if i < len(wow_votes):
            vote_value = wow_votes[i]
            
            # Create vote for WOW-316
            vote, created = Vote.objects.update_or_create(
                participant=participant,
                story=wow_story,
                defaults={'value': vote_value, 'room': room, 'revealed': False}
            )
            
            print(f"  {participant.username:<8} voted: {vote_value:>2}")
            
            if vote_value not in ['?', 'coffee']:
                total_wow += int(vote_value)
    
    avg_wow = total_wow / len(wow_votes)
    rounded_wow = round(avg_wow)
    
    print(f"  📊 Sum: {total_wow}, Average: {avg_wow:.1f} → {rounded_wow}")
    print()
    
    print("🗳️  Adding votes to TEST-123:")
    print("-" * 30)
    
    # Add votes to TEST-123
    total_test = 0
    for i, participant in enumerate(participants):
        if i < len(test_votes):
            vote_value = test_votes[i]
            
            # Create vote for TEST-123
            vote, created = Vote.objects.update_or_create(
                participant=participant,
                story=test_story,
                defaults={'value': vote_value, 'room': room, 'revealed': False}
            )
            
            print(f"  {participant.username:<8} voted: {vote_value:>2}")
            
            if vote_value not in ['?', 'coffee']:
                total_test += int(vote_value)
    
    avg_test = total_test / len(test_votes)
    rounded_test = round(avg_test)
    
    print(f"  📊 Sum: {total_test}, Average: {avg_test:.1f} → {rounded_test}")
    print()
    
    # Set WOW-316 as current for testing
    room.current_story = wow_story
    room.save()
    
    print(f"🎯 Set WOW-316 as current story for testing")
    print()
    
    # Check final room state
    room_response = requests.get(f"{base_url}/api/rooms/{room_code}/")
    room_data = room_response.json()
    
    print("📈 Final Room State:")
    print("-" * 25)
    
    for story in room_data['stories']:
        votes_count = story['votes_count']
        story_id = story['story_id']
        
        if votes_count > 0:
            is_current = "← CURRENT" if story['id'] == room_data['current_story'] else ""
            print(f"  📖 {story_id}: {votes_count} votes {is_current}")
        else:
            print(f"  📖 {story_id}: No votes")
    
    print()
    print("🎉 Votes added successfully!")
    print("📍 Now you can test:")
    print("   • Switch between stories to see votes")
    print("   • Click 'Reveal' on WOW-316 to see average calculation")
    print("   • Test reset functionality on estimated stories")
    
    return {
        'wow_votes': len(wow_votes),
        'test_votes': len(test_votes),
        'wow_average': avg_wow,
        'test_average': avg_test
    }

if __name__ == "__main__":
    try:
        result = add_votes_to_stories()
        print(f"\n✅ Success! Added votes to both stories")
        print(f"   WOW-316: {result['wow_votes']} votes (avg: {result['wow_average']:.1f})")
        print(f"   TEST-123: {result['test_votes']} votes (avg: {result['test_average']:.1f})")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()