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
      <div className="w-full max-w-4xl space-y-8">
        <div className="text-center space-y-2">
          <h1 className="text-4xl font-bold">Planning Poker</h1>
          <p className="text-muted-foreground">Estimate story points with your team in real-time</p>
        </div>

        <div className="grid md:grid-cols-2 gap-6">
          {/* Create Room */}
          <Card>
            <CardHeader>
              <CardTitle>Create Room</CardTitle>
              <CardDescription>Start a new estimation session</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <label className="text-sm font-medium mb-2 block">Your Name *</label>
                <Input
                  placeholder="Enter your name"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                />
              </div>
              <div>
                <label className="text-sm font-medium mb-2 block">Story ID (optional)</label>
                <Input
                  placeholder="e.g., JIRA-123"
                  value={storyId}
                  onChange={(e) => setStoryId(e.target.value)}
                />
              </div>
              <div>
                <label className="text-sm font-medium mb-2 block">Story Title (optional)</label>
                <Input
                  placeholder="e.g., User authentication"
                  value={title}
                  onChange={(e) => setTitle(e.target.value)}
                />
              </div>
              <Button
                className="w-full"
                onClick={handleCreateRoom}
                disabled={isCreating}
              >
                {isCreating ? 'Creating...' : 'Create Room'}
              </Button>
            </CardContent>
          </Card>

          {/* Join Room */}
          <Card>
            <CardHeader>
              <CardTitle>Join Room</CardTitle>
              <CardDescription>Enter an existing room code</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <label className="text-sm font-medium mb-2 block">Your Name *</label>
                <Input
                  placeholder="Enter your name"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                />
              </div>
              <div>
                <label className="text-sm font-medium mb-2 block">Room Code *</label>
                <Input
                  placeholder="e.g., ABC123"
                  value={roomCode}
                  onChange={(e) => setRoomCode(e.target.value.toUpperCase())}
                  maxLength={6}
                />
              </div>
              <Button
                className="w-full mt-[88px]"
                onClick={handleJoinRoom}
                variant="outline"
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
