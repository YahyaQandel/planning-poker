#!/usr/bin/env python3
"""
Restore the lost votes for testing
"""
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from rooms.models import Room, Participant, Vote, Story

def restore_votes():
    room = Room.objects.get(code="XO6ZEG")
    participants = list(Participant.objects.filter(room=room).order_by('joined_at')[:10])
    
    # Restore WOW-316 votes
    story1 = Story.objects.get(room=room, story_id="WOW-316")
    vote_values_1 = ['1', '2', '3', '5', '8', '13', '21', '1', '5', '8']
    
    print("🔄 Restoring votes for WOW-316...")
    for i, participant in enumerate(participants):
        if i < len(vote_values_1):
            vote, created = Vote.objects.update_or_create(
                participant=participant,
                story=story1,
                defaults={'value': vote_values_1[i], 'room': room, 'revealed': True}
            )
            print(f"  {participant.username}: {vote_values_1[i]}")
    
    # Restore TEST-123 votes  
    story2 = Story.objects.get(room=room, story_id="TEST-123")
    vote_values_2 = ['5', '8', '8', '13', '13', '21', '13', '8', '5', '8']
    
    print("\n🔄 Restoring votes for TEST-123...")
    for i, participant in enumerate(participants):
        if i < len(vote_values_2):
            vote, created = Vote.objects.update_or_create(
                participant=participant,
                story=story2,
                defaults={'value': vote_values_2[i], 'room': room, 'revealed': True}
            )
            print(f"  {participant.username}: {vote_values_2[i]}")
    
    print(f"\n✅ Votes restored for both stories!")

if __name__ == "__main__":
    restore_votes()