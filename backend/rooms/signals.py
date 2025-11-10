import logging
import json
from django.db.models.signals import post_save, post_delete, pre_save, pre_delete
from django.dispatch import receiver
from .models import Room, Participant, Story, Vote

# Set up logger
db_logger = logging.getLogger('rooms.database')


@receiver(pre_save, sender=Room)
def room_pre_save(sender, instance, **kwargs):
    """Log before room is saved"""
    if instance.pk:
        db_logger.info(f"DB PRE_SAVE - Updating Room {instance.code}")
    else:
        db_logger.info(f"DB PRE_SAVE - Creating new Room")


@receiver(post_save, sender=Room)
def room_post_save(sender, instance, created, **kwargs):
    """Log after room is saved"""
    if created:
        db_logger.info(f"DB POST_SAVE - Room created: {instance.code} (ID: {instance.id})")
        db_logger.debug(f"DB POST_SAVE - Room data: code={instance.code}, created_at={instance.created_at}")
    else:
        db_logger.info(f"DB POST_SAVE - Room updated: {instance.code} (ID: {instance.id})")
        db_logger.debug(f"DB POST_SAVE - Room data: current_story={instance.current_story}")


@receiver(pre_delete, sender=Room)
def room_pre_delete(sender, instance, **kwargs):
    """Log before room is deleted"""
    db_logger.info(f"DB PRE_DELETE - Deleting Room {instance.code} (ID: {instance.id})")


@receiver(post_delete, sender=Room)
def room_post_delete(sender, instance, **kwargs):
    """Log after room is deleted"""
    db_logger.info(f"DB POST_DELETE - Room deleted: {instance.code}")


@receiver(pre_save, sender=Participant)
def participant_pre_save(sender, instance, **kwargs):
    """Log before participant is saved"""
    room_code = instance.room.code if instance.room else "Unknown"
    if instance.pk:
        db_logger.info(f"DB PRE_SAVE - Updating Participant {instance.username} in room {room_code}")
    else:
        db_logger.info(f"DB PRE_SAVE - Creating new Participant {instance.username} in room {room_code}")


@receiver(post_save, sender=Participant)
def participant_post_save(sender, instance, created, **kwargs):
    """Log after participant is saved"""
    room_code = instance.room.code if instance.room else "Unknown"
    if created:
        db_logger.info(f"DB POST_SAVE - Participant created: {instance.username} in room {room_code} (ID: {instance.id})")
        db_logger.debug(f"DB POST_SAVE - Participant data: username={instance.username}, connected={instance.connected}, session_id={instance.session_id}")
    else:
        db_logger.info(f"DB POST_SAVE - Participant updated: {instance.username} in room {room_code} (ID: {instance.id})")
        db_logger.debug(f"DB POST_SAVE - Participant data: connected={instance.connected}, joined_at={instance.joined_at}")


@receiver(pre_delete, sender=Participant)
def participant_pre_delete(sender, instance, **kwargs):
    """Log before participant is deleted"""
    room_code = instance.room.code if instance.room else "Unknown"
    db_logger.info(f"DB PRE_DELETE - Deleting Participant {instance.username} from room {room_code} (ID: {instance.id})")


@receiver(post_delete, sender=Participant)
def participant_post_delete(sender, instance, **kwargs):
    """Log after participant is deleted"""
    db_logger.info(f"DB POST_DELETE - Participant deleted: {instance.username}")


@receiver(pre_save, sender=Story)
def story_pre_save(sender, instance, **kwargs):
    """Log before story is saved"""
    room_code = instance.room.code if instance.room else "Unknown"
    if instance.pk:
        db_logger.info(f"DB PRE_SAVE - Updating Story {instance.story_id} in room {room_code}")
    else:
        db_logger.info(f"DB PRE_SAVE - Creating new Story {instance.story_id} in room {room_code}")


@receiver(post_save, sender=Story)
def story_post_save(sender, instance, created, **kwargs):
    """Log after story is saved"""
    room_code = instance.room.code if instance.room else "Unknown"
    if created:
        db_logger.info(f"DB POST_SAVE - Story created: '{instance.story_id}' in room {room_code} (ID: {instance.id})")
        db_logger.debug(f"DB POST_SAVE - Story data: story_id={instance.story_id}, title={instance.title}, order={instance.order}")
    else:
        db_logger.info(f"DB POST_SAVE - Story updated: '{instance.story_id}' in room {room_code} (ID: {instance.id})")
        db_logger.debug(f"DB POST_SAVE - Story data: final_points={instance.final_points}, estimated_at={instance.estimated_at}")


@receiver(pre_delete, sender=Story)
def story_pre_delete(sender, instance, **kwargs):
    """Log before story is deleted"""
    room_code = instance.room.code if instance.room else "Unknown"
    db_logger.info(f"DB PRE_DELETE - Deleting Story '{instance.story_id}' from room {room_code} (ID: {instance.id})")


@receiver(post_delete, sender=Story)
def story_post_delete(sender, instance, **kwargs):
    """Log after story is deleted"""
    db_logger.info(f"DB POST_DELETE - Story deleted: '{instance.story_id}'")


@receiver(pre_save, sender=Vote)
def vote_pre_save(sender, instance, **kwargs):
    """Log before vote is saved"""
    room_code = instance.room.code if instance.room else "Unknown"
    participant_name = instance.participant.username if instance.participant else "Unknown"
    story_id = instance.story.story_id if instance.story else "Unknown"
    
    if instance.pk:
        db_logger.info(f"DB PRE_SAVE - Updating Vote by {participant_name} for story '{story_id}' in room {room_code}")
    else:
        db_logger.info(f"DB PRE_SAVE - Creating new Vote by {participant_name} for story '{story_id}' in room {room_code}")


@receiver(post_save, sender=Vote)
def vote_post_save(sender, instance, created, **kwargs):
    """Log after vote is saved"""
    room_code = instance.room.code if instance.room else "Unknown"
    participant_name = instance.participant.username if instance.participant else "Unknown"
    story_id = instance.story.story_id if instance.story else "Unknown"
    
    if created:
        db_logger.info(f"DB POST_SAVE - Vote created: {participant_name} voted '{instance.value}' for story '{story_id}' in room {room_code} (ID: {instance.id})")
        db_logger.debug(f"DB POST_SAVE - Vote data: value={instance.value}, revealed={instance.revealed}, created_at={instance.created_at}")
    else:
        db_logger.info(f"DB POST_SAVE - Vote updated: {participant_name}'s vote for story '{story_id}' in room {room_code} (ID: {instance.id})")
        db_logger.debug(f"DB POST_SAVE - Vote data: value={instance.value}, revealed={instance.revealed}")


@receiver(pre_delete, sender=Vote)
def vote_pre_delete(sender, instance, **kwargs):
    """Log before vote is deleted"""
    room_code = instance.room.code if instance.room else "Unknown"
    participant_name = instance.participant.username if instance.participant else "Unknown"
    story_id = instance.story.story_id if instance.story else "Unknown"
    db_logger.info(f"DB PRE_DELETE - Deleting Vote by {participant_name} for story '{story_id}' in room {room_code} (ID: {instance.id})")


@receiver(post_delete, sender=Vote)
def vote_post_delete(sender, instance, **kwargs):
    """Log after vote is deleted"""
    db_logger.info(f"DB POST_DELETE - Vote deleted: ID {instance.pk}")