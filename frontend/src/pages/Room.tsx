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
  const [existingStory, setExistingStory] = useState<any>(null);
  const [showResetConfirm, setShowResetConfirm] = useState(false);

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
        
        // Restore selected vote if user already voted for current story
        if (data.room.current_story_data?.votes) {
          const myVote = data.room.current_story_data.votes.find(
            (vote: any) => vote.participant === data.participant.id
          );
          if (myVote) {
            setSelectedVote(myVote.value as VoteValue);
          }
        }
        
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
            
            // Restore selected vote if user already voted for current story (on room updates)
            if (data.room.current_story_data?.votes && participantId) {
              const myVote = data.room.current_story_data.votes.find(
                (vote: any) => vote.participant === participantId
              );
              if (myVote && !selectedVote) {
                setSelectedVote(myVote.value as VoteValue);
              }
            }
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

          // Handle existing story detection
          if (data.type === 'story_exists') {
            setExistingStory(data.story);
          }

          // Reset selected vote when room is reset
          if (data.type === 'room_reset') {
            setSelectedVote(null);
            setShowConfirmDialog(false);
            setCalculationResult(null);
            setShowResetConfirm(false);
          }

          // Clear existing story dialog and selected vote when story changes
          if (data.type === 'story_changed') {
            setExistingStory(null);
            setSelectedVote(null);
          }

          // Clear selected vote when new story is added
          if (data.type === 'story_added') {
            setSelectedVote(null);
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
    setShowResetConfirm(true);
  };

  const handleConfirmReset = () => {
    if (!ws || ws.readyState !== WebSocket.OPEN) return;

    setSelectedVote(null);
    setShowResetConfirm(false);

    ws.send(JSON.stringify({
      type: 'reset',
    }));
  };

  const handleCancelReset = () => {
    setShowResetConfirm(false);
  };

  const handleAddStory = () => {
    if (!ws || ws.readyState !== WebSocket.OPEN) return;

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

  const handleSwitchToExistingStory = () => {
    if (!ws || ws.readyState !== WebSocket.OPEN || !existingStory) return;

    ws.send(JSON.stringify({
      type: 'switch_to_existing_story',
      story_id: existingStory.id
    }));

    setExistingStory(null);
  };

  const handleCancelExistingStory = () => {
    setExistingStory(null);
  };

  const handleStoryClick = (storyId: string) => {
    if (!ws || ws.readyState !== WebSocket.OPEN) return;

    ws.send(JSON.stringify({
      type: 'change_story',
      story_id: storyId
    }));
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
    <div className="min-h-screen bg-background p-2 sm:p-4">
      <div className="max-w-7xl mx-auto space-y-4 sm:space-y-6">
        {/* Header */}
        <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4" data-testid="room-header">
          <div className="flex flex-col sm:flex-row sm:items-start gap-3 sm:gap-4">
            <img 
              src="/teracloud_favico.svg" 
              alt="Teracloud Logo" 
              className="w-10 h-10 sm:w-12 sm:h-12 mt-1 flex-shrink-0"
              data-testid="room-logo"
            />
            <div className="min-w-0 flex-1">
              <h1 className="text-xl sm:text-2xl lg:text-3xl font-bold break-words" data-testid="session-name">{room.session_name}</h1>
              <div className="flex flex-col sm:flex-row sm:items-center gap-1 sm:gap-2 mt-1">
                <div className="flex items-center gap-2">
                  <span className="text-xs sm:text-sm text-muted-foreground">Room:</span>
                  <span className="font-mono font-semibold text-sm sm:text-base lg:text-lg" data-testid="room-code">{code}</span>
                  <Button
                    size="sm"
                    variant="ghost"
                    onClick={handleCopyRoomCode}
                    className="h-6 w-6 p-0 sm:h-8 sm:w-8"
                    data-testid="copy-room-code-button"
                  >
                    <Copy className="w-3 h-3 sm:w-4 sm:h-4" />
                  </Button>
                </div>
              </div>
              <div className="mt-1">
                <span className="text-xs sm:text-sm text-muted-foreground">User:</span>
                <span className="font-semibold ml-1 text-sm sm:text-base" data-testid="current-username">{username}</span>
              </div>
            </div>
          </div>
          <div className="flex flex-wrap gap-2">
            <Button
              variant="outline"
              onClick={handleReset}
              disabled={!currentStory}
              size="sm"
              className="text-xs sm:text-sm"
              data-testid="reset-button"
            >
              <RefreshCw className="w-3 h-3 sm:w-4 sm:h-4 mr-1 sm:mr-2" />
              <span className="hidden sm:inline">Reset</span>
            </Button>
            <Button
              onClick={handleReveal}
              disabled={!currentStory || votes.length === 0 || revealed || !allVoted}
              size="sm"
              className="text-xs sm:text-sm"
              data-testid="reveal-button"
            >
              <Eye className="w-3 h-3 sm:w-4 sm:h-4 mr-1 sm:mr-2" />
              Reveal
            </Button>
            <Button
              variant="secondary"
              onClick={() => setShowAddStory(!showAddStory)}
              size="sm"
              className="text-xs sm:text-sm"
              data-testid="add-story-toggle-button"
            >
              <Plus className="w-3 h-3 sm:w-4 sm:h-4 mr-1 sm:mr-2" />
              <span className="hidden sm:inline">Add </span>Story
            </Button>
          </div>
        </div>

        {/* Add Story Form */}
        {showAddStory && (
          <Card data-testid="add-story-form">
            <CardContent className="p-4 space-y-3">
              <div className="flex flex-col sm:flex-row gap-3">
                <Input
                  placeholder="Story ID (optional)"
                  value={newStoryId}
                  onChange={(e) => setNewStoryId(e.target.value)}
                  className="flex-1"
                  data-testid="new-story-id-input"
                />
                <Input
                  placeholder="Story Title (optional)"
                  value={newStoryTitle}
                  onChange={(e) => setNewStoryTitle(e.target.value)}
                  className="flex-1"
                  data-testid="new-story-title-input"
                />
                <div className="flex gap-2">
                  <Button onClick={handleAddStory} size="sm" data-testid="add-story-button">Add</Button>
                  <Button variant="outline" onClick={() => setShowAddStory(false)} size="sm" data-testid="cancel-add-story-button">
                    Cancel
                  </Button>
                </div>
              </div>
              <div className="text-xs text-muted-foreground bg-muted/50 p-2 rounded" data-testid="add-story-tip">
                💡 Leave empty for a randomly generated funny story!
              </div>
            </CardContent>
          </Card>
        )}

        {/* Existing Story Confirmation */}
        {existingStory && (
          <Card className="border-orange-500 bg-orange-50" data-testid="existing-story-dialog">
            <CardContent className="p-4">
              <div className="space-y-3">
                <div>
                  <div className="font-semibold text-lg" data-testid="existing-story-title">Story Already Exists</div>
                  <div className="text-sm text-muted-foreground mt-1">
                    Story ID "{existingStory.story_id}" already exists
                    {existingStory.final_points && (
                      <span className="font-medium"> with {existingStory.final_points} points</span>
                    )}
                  </div>
                </div>
                <div className="flex gap-2">
                  <Button
                    variant="outline"
                    onClick={handleCancelExistingStory}
                    className="flex-1"
                    data-testid="cancel-existing-story-button"
                  >
                    Cancel
                  </Button>
                  <Button
                    onClick={handleSwitchToExistingStory}
                    className="flex-1"
                    data-testid="switch-to-existing-story-button"
                  >
                    Switch to This Story
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Reset Confirmation Dialog */}
        {showResetConfirm && (
          <Card className="border-red-500 bg-red-50" data-testid="reset-confirm-dialog">
            <CardContent className="p-4">
              <div className="space-y-3">
                <div>
                  <div className="font-semibold text-lg text-red-700" data-testid="reset-confirm-title">Reset All Votes?</div>
                  <div className="text-sm text-red-600 mt-1">
                    This will clear all votes for the current story. Everyone will need to vote again.
                  </div>
                </div>
                <div className="flex gap-2">
                  <Button
                    variant="outline"
                    onClick={handleCancelReset}
                    className="flex-1"
                    data-testid="cancel-reset-button"
                  >
                    Cancel
                  </Button>
                  <Button
                    variant="destructive"
                    onClick={handleConfirmReset}
                    className="flex-1"
                    data-testid="confirm-reset-button"
                  >
                    Reset All Votes
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-12 gap-4 lg:gap-6">
          {/* Left Sidebar - Stories */}
          <div className="lg:col-span-3 order-3 lg:order-1">
            <StorySidebar 
              stories={room.stories} 
              currentStoryId={room.current_story}
              onStoryClick={handleStoryClick}
            />
          </div>

          {/* Main Content */}
          <div className="lg:col-span-6 order-1 lg:order-2">
            <CurrentStory story={currentStory} />

            {/* Voting Status */}
            {currentStory && (
              <Card className="mb-6" data-testid="voting-status">
                <CardContent className="p-4">
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-muted-foreground" data-testid="vote-count">
                      {votes.length} / {room.participants.filter(p => p.connected).length} voted
                    </span>
                    {allVoted && !revealed && (
                      <span className="text-sm font-medium text-green-600" data-testid="all-voted-indicator">
                        Everyone has voted!
                      </span>
                    )}
                  </div>
                </CardContent>
              </Card>
            )}

            {/* Voting Cards */}
            <div className="space-y-3 sm:space-y-4" data-testid="voting-section">
              <h2 className="text-lg sm:text-xl font-semibold" data-testid="voting-section-title">Cast Your Vote</h2>
              <div className="grid grid-cols-5 sm:flex sm:flex-wrap gap-2 sm:gap-3" data-testid="voting-cards-container">
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
          <div className="lg:col-span-3 order-2 lg:order-3">
            <ParticipantList
              participants={room.participants}
              votes={votes}
              revealed={revealed}
            />

            {/* Confirmation UI */}
            {showConfirmDialog && calculationResult && (
              <div data-testid="confirm-points-dialog">
                <ConfirmPointsDialog
                  average={calculationResult.average}
                  rounded={calculationResult.rounded}
                  onConfirm={handleConfirmPoints}
                  onReject={handleRejectPoints}
                />
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
