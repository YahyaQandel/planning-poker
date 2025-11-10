import { useEffect, useState } from 'react';
import { useParams, useSearchParams, useNavigate } from 'react-router-dom';
import { Copy, RefreshCw, Eye, Plus } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent } from '@/components/ui/card';
import VotingCard from '@/components/VotingCard';
import ParticipantList from '@/components/ParticipantList';
import StorySidebar from '@/components/StorySidebar';
import CurrentStory from '@/components/CurrentStory';
import ConfirmPointsDialog from '@/components/ConfirmPointsDialog';
import type { Room as RoomType, VoteValue } from '@/types/index';
import { VOTE_OPTIONS } from '@/types/index';

export default function Room() {
  const { code } = useParams<{ code: string }>();
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const username = searchParams.get('username');

  const [room, setRoom] = useState<RoomType | null>(null);
  const [selectedVote, setSelectedVote] = useState<VoteValue | null>(null);
  const [participantId, setParticipantId] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [showAddStory, setShowAddStory] = useState(false);
  const [newStoryId, setNewStoryId] = useState('');
  const [newStoryTitle, setNewStoryTitle] = useState('');
  const [ws, setWs] = useState<WebSocket | null>(null);
  const [showConfirmDialog, setShowConfirmDialog] = useState(false);
  const [calculationResult, setCalculationResult] = useState<{average: number, rounded: number} | null>(null);

  useEffect(() => {
    if (!username) {
      navigate('/');
      return;
    }

    let websocket: WebSocket | null = null;

    const joinRoom = async () => {
      try {
        // Join room via REST API
        const response = await fetch(`http://localhost:8000/api/rooms/${code}/join/`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            username,
            session_id: `${username}-${Date.now()}`,
          }),
        });

        if (!response.ok) {
          throw new Error('Room not found');
        }

        const data = await response.json();
        setRoom(data.room);
        setParticipantId(data.participant.id);
        setLoading(false);

        // Connect to WebSocket
        websocket = new WebSocket(`ws://localhost:8000/ws/room/${code}/`);

        websocket.onopen = () => {
          console.log('WebSocket connected');
          // Notify others that user joined
          websocket?.send(JSON.stringify({
            type: 'user_joined',
            username,
          }));
        };

        websocket.onmessage = (event) => {
          const data = JSON.parse(event.data);
          console.log('WebSocket message:', data);

          if (data.room) {
            setRoom(data.room);
          }

          // Show confirmation dialog when votes are revealed with average
          if (data.type === 'votes_revealed' && data.average !== null) {
            setCalculationResult({
              average: data.average,
              rounded: data.rounded
            });
            setShowConfirmDialog(true);
          }

          // Hide dialog and clear result when points are confirmed
          if (data.type === 'points_confirmed') {
            setShowConfirmDialog(false);
            setCalculationResult(null);
          }

          // Reset selected vote when room is reset
          if (data.type === 'room_reset') {
            setSelectedVote(null);
            setShowConfirmDialog(false);
            setCalculationResult(null);
          }
        };

        websocket.onerror = (error) => {
          console.error('WebSocket error:', error);
        };

        websocket.onclose = () => {
          console.log('WebSocket disconnected');
        };

        setWs(websocket);
      } catch (error) {
        console.error('Error joining room:', error);
        alert('Failed to join room');
        navigate('/');
      }
    };

    joinRoom();

    // Cleanup function
    return () => {
      if (websocket && websocket.readyState === WebSocket.OPEN) {
        websocket.close();
      }
    };
  }, [code, username, navigate]);

  const handleVote = (value: VoteValue) => {
    if (!room?.current_story || !participantId || !ws || ws.readyState !== WebSocket.OPEN) return;

    setSelectedVote(value);

    ws.send(JSON.stringify({
      type: 'vote',
      participant_id: participantId,
      story_id: room.current_story,
      value,
    }));
  };

  const handleReveal = () => {
    if (!ws || ws.readyState !== WebSocket.OPEN) return;

    ws.send(JSON.stringify({
      type: 'reveal',
    }));
  };

  const handleReset = () => {
    if (!ws || ws.readyState !== WebSocket.OPEN) return;

    setSelectedVote(null);

    ws.send(JSON.stringify({
      type: 'reset',
    }));
  };

  const handleAddStory = () => {
    if (!ws || ws.readyState !== WebSocket.OPEN || (!newStoryId && !newStoryTitle)) return;

    ws.send(JSON.stringify({
      type: 'add_story',
      story_id: newStoryId || '',
      title: newStoryTitle || '',
    }));

    setNewStoryId('');
    setNewStoryTitle('');
    setShowAddStory(false);
  };

  const handleCopyRoomCode = () => {
    navigator.clipboard.writeText(code || '');
    alert('Room code copied to clipboard!');
  };

  const handleConfirmPoints = () => {
    if (!ws || ws.readyState !== WebSocket.OPEN || !calculationResult) return;

    ws.send(JSON.stringify({
      type: 'confirm_points',
      points: calculationResult.rounded
    }));
  };

  const handleRejectPoints = () => {
    if (!ws || ws.readyState !== WebSocket.OPEN) return;

    ws.send(JSON.stringify({
      type: 'reset'
    }));

    setShowConfirmDialog(false);
    setCalculationResult(null);
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="text-center">
          <div className="text-xl font-semibold">Joining room...</div>
        </div>
      </div>
    );
  }

  if (!room) {
    return null;
  }

  const currentStory = room.current_story_data;
  const votes = currentStory?.votes || [];
  const revealed = votes.length > 0 && votes[0]?.revealed;
  const allVoted = room.participants.filter(p => p.connected).every(p =>
    votes.some(v => v.participant === p.id)
  );

  return (
    <div className="min-h-screen bg-background p-4">
      <div className="max-w-7xl mx-auto space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold">Planning Poker</h1>
            <div className="flex items-center gap-2 mt-1">
              <span className="text-muted-foreground">Room:</span>
              <span className="font-mono font-semibold text-lg">{code}</span>
              <Button
                size="sm"
                variant="ghost"
                onClick={handleCopyRoomCode}
              >
                <Copy className="w-4 h-4" />
              </Button>
            </div>
          </div>
          <div className="flex gap-2">
            <Button
              variant="outline"
              onClick={handleReset}
              disabled={!currentStory}
            >
              <RefreshCw className="w-4 h-4 mr-2" />
              Reset
            </Button>
            <Button
              onClick={handleReveal}
              disabled={!currentStory || votes.length === 0 || revealed}
            >
              <Eye className="w-4 h-4 mr-2" />
              Reveal
            </Button>
            <Button
              variant="secondary"
              onClick={() => setShowAddStory(!showAddStory)}
            >
              <Plus className="w-4 h-4 mr-2" />
              Add Story
            </Button>
          </div>
        </div>

        {/* Add Story Form */}
        {showAddStory && (
          <Card>
            <CardContent className="p-4">
              <div className="flex gap-3">
                <Input
                  placeholder="Story ID (optional)"
                  value={newStoryId}
                  onChange={(e) => setNewStoryId(e.target.value)}
                />
                <Input
                  placeholder="Story Title (optional)"
                  value={newStoryTitle}
                  onChange={(e) => setNewStoryTitle(e.target.value)}
                />
                <Button onClick={handleAddStory}>Add</Button>
                <Button variant="outline" onClick={() => setShowAddStory(false)}>
                  Cancel
                </Button>
              </div>
            </CardContent>
          </Card>
        )}

        <div className="grid grid-cols-12 gap-6">
          {/* Left Sidebar - Stories */}
          <div className="col-span-3">
            <StorySidebar stories={room.stories} />
          </div>

          {/* Main Content */}
          <div className="col-span-6">
            <CurrentStory story={currentStory} />

            {/* Voting Status */}
            {currentStory && (
              <Card className="mb-6">
                <CardContent className="p-4">
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-muted-foreground">
                      {votes.length} / {room.participants.filter(p => p.connected).length} voted
                    </span>
                    {allVoted && !revealed && (
                      <span className="text-sm font-medium text-green-600">
                        Everyone has voted!
                      </span>
                    )}
                  </div>
                </CardContent>
              </Card>
            )}

            {/* Voting Cards */}
            <div className="space-y-4">
              <h2 className="text-xl font-semibold">Cast Your Vote</h2>
              <div className="flex gap-3 flex-wrap">
                {VOTE_OPTIONS.map((value) => (
                  <VotingCard
                    key={value}
                    value={value}
                    selected={selectedVote === value}
                    onClick={() => handleVote(value)}
                    disabled={!currentStory || revealed}
                  />
                ))}
              </div>
            </div>
          </div>

          {/* Right Sidebar - Participants */}
          <div className="col-span-3">
            <ParticipantList
              participants={room.participants}
              votes={votes}
              revealed={revealed}
            />

            {/* Confirmation UI */}
            {showConfirmDialog && calculationResult && (
              <ConfirmPointsDialog
                average={calculationResult.average}
                rounded={calculationResult.rounded}
                onConfirm={handleConfirmPoints}
                onReject={handleRejectPoints}
              />
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
