import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';

export default function Home() {
  const [username, setUsername] = useState('');
  const [storyId, setStoryId] = useState('');
  const [title, setTitle] = useState('');
  const [roomCode, setRoomCode] = useState('');
  const [isCreating, setIsCreating] = useState(false);
  const navigate = useNavigate();

  const handleCreateRoom = async () => {
    if (!username.trim()) {
      alert('Please enter your name');
      return;
    }

    setIsCreating(true);
    try {
      const response = await fetch('http://localhost:8000/api/rooms/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          story_id: storyId || undefined,
          title: title || undefined,
        }),
      });

      const data = await response.json();
      navigate(`/room/${data.code}?username=${encodeURIComponent(username)}`);
    } catch (error) {
      console.error('Error creating room:', error);
      alert('Failed to create room');
    } finally {
      setIsCreating(false);
    }
  };

  const handleJoinRoom = () => {
    if (!username.trim()) {
      alert('Please enter your name');
      return;
    }
    if (!roomCode.trim()) {
      alert('Please enter room code');
      return;
    }

    navigate(`/room/${roomCode.toUpperCase()}?username=${encodeURIComponent(username)}`);
  };

  return (
    <div className="min-h-screen bg-background flex items-center justify-center p-4">
      <div className="w-full max-w-4xl space-y-6 md:space-y-8">
        <div className="text-center space-y-3 md:space-y-4" data-testid="home-header">
          <div className="flex flex-col sm:flex-row items-center justify-center gap-3 md:gap-4">
            <img 
              src="/teracloud_favico.svg" 
              alt="Teracloud Logo" 
              className="w-12 h-12 sm:w-14 sm:h-14 md:w-16 md:h-16"
              data-testid="teracloud-logo"
            />
            <h1 className="text-2xl sm:text-3xl md:text-4xl font-bold" data-testid="app-title">Planning Poker</h1>
          </div>
          <p className="text-sm sm:text-base text-muted-foreground px-4" data-testid="app-description">Estimate story points with your team in real-time</p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 md:gap-6">
          {/* Create Room */}
          <Card data-testid="create-room-card">
            <CardHeader>
              <CardTitle data-testid="create-room-title">Create Room</CardTitle>
              <CardDescription data-testid="create-room-description">Start a new estimation session</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <label className="text-sm font-medium mb-2 block" data-testid="create-username-label">Your Name *</label>
                <Input
                  placeholder="Enter your name"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  data-testid="create-username-input"
                />
              </div>
              <div>
                <label className="text-sm font-medium mb-2 block" data-testid="create-story-id-label">Story ID (optional)</label>
                <Input
                  placeholder="e.g., JIRA-123"
                  value={storyId}
                  onChange={(e) => setStoryId(e.target.value)}
                  data-testid="create-story-id-input"
                />
              </div>
              <div>
                <label className="text-sm font-medium mb-2 block" data-testid="create-story-title-label">Story Title (optional)</label>
                <Input
                  placeholder="e.g., User authentication"
                  value={title}
                  onChange={(e) => setTitle(e.target.value)}
                  data-testid="create-story-title-input"
                />
              </div>
              <div className="text-xs text-muted-foreground bg-muted/50 p-2 rounded" data-testid="create-room-tip">
                💡 Tip: Leave both fields empty and we'll create a fun, randomly generated story for you!
              </div>
              <Button
                className="w-full"
                onClick={handleCreateRoom}
                disabled={isCreating}
                data-testid="create-room-button"
              >
                {isCreating ? 'Creating...' : 'Create Room'}
              </Button>
            </CardContent>
          </Card>

          {/* Join Room */}
          <Card data-testid="join-room-card">
            <CardHeader>
              <CardTitle data-testid="join-room-title">Join Room</CardTitle>
              <CardDescription data-testid="join-room-description">Enter an existing room code</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <label className="text-sm font-medium mb-2 block" data-testid="join-username-label">Your Name *</label>
                <Input
                  placeholder="Enter your name"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  data-testid="join-username-input"
                />
              </div>
              <div>
                <label className="text-sm font-medium mb-2 block" data-testid="join-room-code-label">Room Code *</label>
                <Input
                  placeholder="e.g., ABC123"
                  value={roomCode}
                  onChange={(e) => setRoomCode(e.target.value.toUpperCase())}
                  maxLength={6}
                  data-testid="join-room-code-input"
                />
              </div>
              <Button
                className="w-full mt-[88px]"
                onClick={handleJoinRoom}
                variant="outline"
                data-testid="join-room-button"
              >
                Join Room
              </Button>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
