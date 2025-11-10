#!/usr/bin/env python3
"""
Test the reset fix for estimated stories
"""
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

import requests
from rooms.models import Room, Story

def test_reset_fix():
    room_code = "XO6ZEG"
    base_url = "http://localhost:8000"
    
    # Get room
    room = Room.objects.get(code=room_code)
    
    # Switch to an estimated story (WOW-316)
    wow_story = Story.objects.get(room=room, story_id="WOW-316")
    print(f"📖 Switching to estimated story: {wow_story.story_id}")
    print(f"   Current points: {wow_story.final_points}")
    print(f"   Votes count: {wow_story.votes.count()}")
    
    # Set as current story
    room.current_story = wow_story
    room.save()
    
    print(f"\n🔄 Testing reset on estimated story...")
    
    # Call reset API
    response = requests.post(f"{base_url}/api/rooms/{room_code}/reset/")
    
    if response.status_code == 200:
        print("✅ Reset API call successful")
        
        # Check story state after reset
        wow_story.refresh_from_db()
        
        print(f"\n📊 After Reset:")
        print(f"   Final points: {wow_story.final_points}")
        print(f"   Estimated at: {wow_story.estimated_at}")
        print(f"   Votes count: {wow_story.votes.count()}")
        
        if wow_story.final_points is None:
            print("✅ Story points correctly cleared!")
        else:
            print("❌ Story points NOT cleared - still has points!")
            
        if wow_story.votes.count() == 0:
            print("✅ Votes correctly cleared!")
        else:
            print("❌ Votes NOT cleared!")
            
    else:
        print(f"❌ Reset failed: {response.status_code}")
        
    # Check room state
    room_response = requests.get(f"{base_url}/api/rooms/{room_code}/")
    room_data = room_response.json()
    
    current_story_data = room_data['current_story_data']
    print(f"\n🏠 Room State:")
    print(f"   Current story: {current_story_data['story_id']}")
    print(f"   Has final_points: {current_story_data['final_points']}")
    print(f"   Votes count: {current_story_data['votes_count']}")
    
    # Check stories sidebar data
    wow_story_data = None
    for story in room_data['stories']:
        if story['story_id'] == 'WOW-316':
            wow_story_data = story
            break
    
    print(f"\n📋 Stories Sidebar:")
    if wow_story_data:
        print(f"   WOW-316 points: {wow_story_data['final_points']}")
        print(f"   WOW-316 votes: {wow_story_data['votes_count']}")
        
        if wow_story_data['final_points'] is None:
            print("✅ Sidebar correctly shows no points!")
        else:
            print("❌ Sidebar still shows points!")
    
    return wow_story_data

if __name__ == "__main__":
    test_reset_fix()