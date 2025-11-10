import uuid
import secrets
import string
import random
from datetime import datetime
from django.db import models
from django.utils import timezone


def generate_room_code():
    """Generate a random 6-character room code"""
    return ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(6))


def generate_session_name():
    """Generate default session name with today's date"""
    today = datetime.now().strftime("%B %d, %Y")
    return f"Planning Session For {today}"


def generate_funny_story():
    """Generate a random funny story with creative ID and title"""
    
    # Funny adjectives (51 items - tripled)
    adjectives = [
        "Epic", "Mysterious", "Hilarious", "Sneaky", "Magical", "Legendary", 
        "Invisible", "Dancing", "Confused", "Caffeinated", "Procrastinating",
        "Rebellious", "Mischievous", "Grumpy", "Sleepy", "Dramatic", "Sarcastic",
        "Brilliant", "Chaotic", "Energetic", "Fierce", "Gigantic", "Heroic",
        "Incredible", "Jolly", "Kinetic", "Lazy", "Mystical", "Naughty",
        "Outstanding", "Peculiar", "Quirky", "Ridiculous", "Spectacular", "Tremendous",
        "Unstoppable", "Vibrant", "Wacky", "Xenial", "Youthful", "Zealous",
        "Bouncy", "Clumsy", "Dreamy", "Eccentric", "Funky", "Goofy", "Happy",
        "Hyper", "Imaginative", "Jovial", "Kooky"
    ]
    
    # Funny nouns/animals (57 items - tripled)
    nouns = [
        "Unicorn", "Penguin", "Dragon", "Ninja", "Pirate", "Robot", "Wizard",
        "Llama", "Narwhal", "Platypus", "Sloth", "Flamingo", "Hedgehog", 
        "Octopus", "Giraffe", "Kangaroo", "Panda", "Walrus", "Manatee",
        "Koala", "Otter", "Alpaca", "Beaver", "Chinchilla", "Dolphin", "Elephant",
        "Fox", "Goose", "Hamster", "Iguana", "Jellyfish", "Kiwi",
        "Lemur", "Mongoose", "Newt", "Ocelot", "Parrot", "Quokka", "Raccoon",
        "Seahorse", "Toucan", "Umbrellabird", "Vulture", "Whale", "Xerus",
        "Yak", "Zebra", "Armadillo", "Butterfly", "Caterpillar", "Dragonfly",
        "Firefly", "Grasshopper", "Hummingbird", "Lobster", "Mantis", "Starfish"
    ]
    
    # Funny actions/tasks (48 items - tripled)
    actions = [
        "Learns to Code", "Drinks Coffee", "Writes Tests", "Debugs Life",
        "Conquers Bugs", "Deploys to Space", "Refactors Reality", 
        "Implements Magic", "Optimizes Dreams", "Merges Chaos",
        "Commits Jokes", "Pushes Boundaries", "Reviews Universe",
        "Scales Mountains", "Encrypts Secrets", "Caches Wisdom",
        "Builds Castles", "Chases Rainbows", "Dances with Code", "Explores Galaxies",
        "Fights Dragons", "Guards Treasures", "Hunts Unicorns", "Invents Time Travel",
        "Juggles Responsibilities", "Keeps Secrets", "Launches Rockets", "Makes Magic",
        "Navigates Storms", "Opens Portals", "Paints Masterpieces", "Questions Reality",
        "Races Lightning", "Sings Lullabies", "Teaches Wisdom", "Unlocks Mysteries",
        "Visits Dimensions", "Weaves Stories", "Xeroxes Dreams", "Yells at Clouds",
        "Zones Out Completely", "Automates Everything", "Bridges Worlds", "Creates Wonders",
        "Dazzles Audiences", "Energizes Teams", "Fixes Everything", "Generates Ideas",
        "Hacks Reality"
    ]
    
    # Team prefixes for story IDs (27 items - tripled)
    prefixes = [
        "EPIC", "LOL", "FUN", "WOW", "OMG", "YAY", "ZAP", "POW", "BOOM",
        "COOL", "NICE", "STAR", "FIRE", "ROCK", "JAZZ", "WILD", "MEGA", "SUPER",
        "ZOOM", "DASH", "BUZZ", "FIZZ", "GLOW", "SNAP", "FLEX", "VIBE", "BEAM"
    ]
    
    # Generate random story
    adjective = random.choice(adjectives)
    noun = random.choice(nouns)
    action = random.choice(actions)
    prefix = random.choice(prefixes)
    story_number = random.randint(100, 999)
    
    story_id = f"{prefix}-{story_number}"
    title = f"The {adjective} {noun} {action}"
    
    return story_id, title


class Room(models.Model):
    code = models.CharField(max_length=6, unique=True, default=generate_room_code, db_index=True)
    session_name = models.CharField(max_length=255, default=generate_session_name)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    current_story = models.ForeignKey('Story', on_delete=models.SET_NULL, null=True, blank=True, related_name='active_in_room')

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Room {self.code}"


class Participant(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='participants')
    username = models.CharField(max_length=50)
    session_id = models.CharField(max_length=100, unique=True)
    connected = models.BooleanField(default=True)
    joined_at = models.DateTimeField(auto_now_add=True)
    last_seen = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['joined_at']
        unique_together = [['room', 'username']]

    def __str__(self):
        return f"{self.username} in {self.room.code}"


class Story(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='stories')
    story_id = models.CharField(max_length=100, blank=True, null=True)
    title = models.CharField(max_length=255, blank=True, null=True)
    final_points = models.CharField(max_length=10, blank=True, null=True)
    estimated_at = models.DateTimeField(null=True, blank=True)
    order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order', 'created_at']
        verbose_name_plural = 'Stories'

    def __str__(self):
        display = self.story_id or self.title or 'Untitled'
        return f"{display} in {self.room.code}"


class Vote(models.Model):
    VOTE_CHOICES = [
        ('0', '0'),
        ('1', '1'),
        ('2', '2'),
        ('3', '3'),
        ('5', '5'),
        ('8', '8'),
        ('13', '13'),
        ('21', '21'),
        ('?', '?'),
        ('coffee', '☕'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='votes')
    participant = models.ForeignKey(Participant, on_delete=models.CASCADE, related_name='votes')
    story = models.ForeignKey(Story, on_delete=models.CASCADE, related_name='votes')
    value = models.CharField(max_length=10, choices=VOTE_CHOICES)
    revealed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['created_at']
        unique_together = [['participant', 'story']]

    def __str__(self):
        return f"{self.participant.username} voted {self.value} for {self.story}"
