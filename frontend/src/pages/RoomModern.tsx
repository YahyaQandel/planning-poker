import React, { useState, useEffect, useRef, useCallback } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Plus, 
  RefreshCw, 
  Eye, 
  LogOut,
  CheckCircle,
  XCircle,
  Layers,
  Users
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from '@/components/ui/alert-dialog';
import { useToast } from '@/components/ui/use-toast';
import StoryCard from '@/components/modern/StoryCard';
import VoteCard from '@/components/modern/VoteCard';
import ParticipantCard from '@/components/modern/ParticipantCard';
import HeaderBar from '@/components/modern/HeaderBar';
import { cn } from '@/lib/utils';

interface Room {
  code: string;
  session_name: string;
  current_story: string | null;
  created_at: string;
  participants: Participant[];
  stories: Story[];
  current_story_data?: Story;
}

interface Participant {
  id: string;
  username: string;
  connected: boolean;
  joined_at: string;
  session_id: string;
}

interface Story {
  id: string;
  story_id: string;
  title: string;
  final_points: string | null;
  votes: Vote[];
  votes_count: number;
  estimated_at: string | null;
}

interface Vote {
  id: string;
  participant: string;
  value: string;
  revealed: boolean;
}

const voteOptions = ['1', '2', '3', '5', '8', '13', '21', '?', 'coffee'];

function RoomModern() {
  const { code } = useParams<{ code: string }>();
  const navigate = useNavigate();
  const { toast } = useToast();
  const [room, setRoom] = useState<Room | null>(null);
  const [ws, setWs] = useState<WebSocket | null>(null);
  const [selectedVote, setSelectedVote] = useState<string | null>(null);
  const [showAddStory, setShowAddStory] = useState(false);
  const [showResetConfirm, setShowResetConfirm] = useState(false);
  const [showExistingStoryDialog, setShowExistingStoryDialog] = useState(false);
  const [existingStory, setExistingStory] = useState<any>(null);
  const [showAverageModal, setShowAverageModal] = useState(false);
  const [averageData, setAverageData] = useState<{ average: number; rounded: number } | null>(null);
  const [newStory, setNewStory] = useState({ story_id: '', title: '' });
  const wsRef = useRef<WebSocket | null>(null);

  const currentParticipantId = localStorage.getItem('participant_id');
  const currentUsername = localStorage.getItem('username');
  const currentSessionId = localStorage.getItem('session_id');

  // Fetch room data
  useEffect(() => {
    const fetchRoom = async () => {
      try {
        const response = await fetch(`${import.meta.env.VITE_API_URL}/rooms/${code}/`);
        if (response.ok) {
          const data = await response.json();
          setRoom(data);
        } else {
          navigate('/');
        }
      } catch (error) {
        console.error('Failed to fetch room:', error);
        navigate('/');
      }
    };

    fetchRoom();
  }, [code, navigate]);

  // WebSocket connection
  useEffect(() => {
    if (!code || !currentParticipantId) return;

    const wsUrl = `${import.meta.env.VITE_WS_URL}/ws/room/${code}/`;
    const websocket = new WebSocket(wsUrl);
    
    websocket.onopen = () => {
      console.log('WebSocket connected');
      websocket.send(JSON.stringify({
        type: 'user_joined',
        username: currentUsername
      }));
    };

    websocket.onmessage = (event) => {
      const data = JSON.parse(event.data);
      handleWebSocketMessage(data);
    };

    websocket.onclose = () => {
      console.log('WebSocket disconnected');
    };

    websocket.onerror = (error) => {
      console.error('WebSocket error:', error);
    };

    wsRef.current = websocket;
    setWs(websocket);

    return () => {
      if (websocket.readyState === WebSocket.OPEN) {
        websocket.send(JSON.stringify({
          type: 'user_left',
          participant_id: currentParticipantId
        }));
      }
      websocket.close();
    };
  }, [code, currentParticipantId, currentUsername]);

  const handleWebSocketMessage = (data: any) => {
    switch (data.type) {
      case 'vote_cast':
      case 'room_reset':
      case 'story_changed':
      case 'story_added':
      case 'user_joined':
      case 'user_left':
      case 'points_confirmed':
        setRoom(data.room);
        break;
      case 'votes_revealed':
        setRoom(data.room);
        if (data.average && data.rounded) {
          setAverageData({ average: data.average, rounded: data.rounded });
          setShowAverageModal(true);
        }
        break;
      case 'story_exists':
        setExistingStory(data.story);
        setShowExistingStoryDialog(true);
        break;
    }
  };

  const handleVote = (value: string) => {
    if (!ws || ws.readyState !== WebSocket.OPEN || !room?.current_story_data) return;
    
    setSelectedVote(value);
    ws.send(JSON.stringify({
      type: 'vote',
      participant_id: currentParticipantId,
      story_id: room.current_story_data.id,
      value: value
    }));
  };

  const handleReveal = () => {
    if (!ws || ws.readyState !== WebSocket.OPEN) return;
    ws.send(JSON.stringify({ type: 'reveal' }));
  };

  const handleReset = () => {
    setShowResetConfirm(true);
  };

  const handleConfirmReset = () => {
    if (!ws || ws.readyState !== WebSocket.OPEN) return;
    setSelectedVote(null);
    setShowResetConfirm(false);
    ws.send(JSON.stringify({ type: 'reset' }));
  };

  const handleAddStory = () => {
    if (!ws || ws.readyState !== WebSocket.OPEN) return;
    
    ws.send(JSON.stringify({
      type: 'add_story',
      story_id: newStory.story_id,
      title: newStory.title
    }));
    
    setNewStory({ story_id: '', title: '' });
    setShowAddStory(false);
  };

  const handleStoryClick = (storyId: string) => {
    if (!ws || ws.readyState !== WebSocket.OPEN) return;
    ws.send(JSON.stringify({
      type: 'change_story',
      story_id: storyId
    }));
  };

  const handleCopyCode = () => {
    if (room?.code) {
      navigator.clipboard.writeText(room.code);
      toast({
        title: "Room code copied!",
        description: `Share ${room.code} with your team`,
      });
    }
  };

  const handleConfirmPoints = (points: number) => {
    if (!ws || ws.readyState !== WebSocket.OPEN) return;
    ws.send(JSON.stringify({
      type: 'confirm_points',
      points: points.toString()
    }));
    setShowAverageModal(false);
    setAverageData(null);
  };

  const handleLeaveRoom = () => {
    localStorage.removeItem('participant_id');
    localStorage.removeItem('username');
    localStorage.removeItem('session_id');
    navigate('/');
  };

  if (!room) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-pulse text-lg">Loading room...</div>
      </div>
    );
  }

  const totalPoints = room.stories.reduce(
    (sum, story) => sum + (story.final_points ? parseInt(story.final_points) : 0),
    0
  );
  const estimatedStories = room.stories.filter(s => s.final_points).length;
  const allParticipantsVoted = room.current_story_data && 
    room.participants.filter(p => p.connected).length > 0 &&
    room.participants.filter(p => p.connected).every(p => 
      room.current_story_data!.votes.some(v => v.participant === p.id)
    );
  const votesRevealed = room.current_story_data?.votes.some(v => v.revealed) || false;

  return (
    <div className="min-h-screen p-4 md:p-6 lg:p-8">
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.5 }}
        className="max-w-[1600px] mx-auto space-y-6"
      >
        {/* Header */}
        <HeaderBar
          sessionName={room.session_name}
          roomCode={room.code}
          totalPoints={totalPoints}
          estimatedStories={estimatedStories}
          totalStories={room.stories.length}
          participantsCount={room.participants.filter(p => p.connected).length}
          onCopyCode={handleCopyCode}
        />

        {/* Main Content Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
          {/* Stories Sidebar */}
          <div className="lg:col-span-3 space-y-4">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-semibold flex items-center gap-2 bg-gradient-to-r from-purple-600 to-indigo-600 bg-clip-text text-transparent">
                <Layers className="w-5 h-5 text-purple-600" />
                Stories
              </h2>
              <Button
                onClick={() => setShowAddStory(true)}
                size="sm"
                className="bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-700 hover:to-indigo-700"
                data-testid="add-story-button"
              >
                <Plus className="w-4 h-4 mr-1" />
                Add
              </Button>
            </div>
            
            <div className="space-y-3 max-h-[600px] overflow-y-auto pr-2">
              {room.stories.map((story, index) => (
                <StoryCard
                  key={story.id}
                  storyId={story.story_id}
                  title={story.title}
                  finalPoints={story.final_points || undefined}
                  votesCount={story.votes_count}
                  isCurrentStory={story.id === room.current_story}
                  onClick={() => handleStoryClick(story.id)}
                />
              ))}
              
              {room.stories.length === 0 && (
                <div className="text-center py-8 text-purple-700">
                  No stories yet. Add your first story to begin!
                </div>
              )}
            </div>

          </div>

          {/* Main Voting Area */}
          <div className="lg:col-span-6 space-y-6">
            {/* Current Story Display */}
            {room.current_story_data && (
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="p-6 rounded-2xl bg-gradient-to-br from-white via-purple-50/50 to-purple-100/50 backdrop-blur-sm border-2 border-purple-200 shadow-xl"
              >
                <div className="text-center space-y-2">
                  <h3 className="text-2xl font-bold bg-gradient-to-r from-purple-600 to-indigo-600 bg-clip-text text-transparent">
                    Currently Estimating
                  </h3>
                  <p className="text-xl font-semibold text-purple-800">
                    {room.current_story_data.story_id}: {room.current_story_data.title}
                  </p>
                  <p className="text-sm text-purple-700">
                    {room.current_story_data.votes_count} of {room.participants.filter(p => p.connected).length} voted
                  </p>
                </div>

                {/* Action Buttons */}
                <div className="flex justify-center gap-3 mt-6">
                  <Button
                    onClick={handleReset}
                    variant="outline"
                    className="border-red-500 text-red-500 hover:bg-red-50 dark:hover:bg-red-950"
                    data-testid="reset-button"
                  >
                    <RefreshCw className="w-4 h-4 mr-2" />
                    Reset
                  </Button>
                  <Button
                    onClick={handleReveal}
                    disabled={!allParticipantsVoted || votesRevealed}
                    className="bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-700 hover:to-indigo-700 disabled:opacity-50"
                    data-testid="reveal-button"
                  >
                    <Eye className="w-4 h-4 mr-2" />
                    Reveal
                  </Button>
                </div>
              </motion.div>
            )}

            {/* Voting Cards */}
            <div className="space-y-4">
              <h3 className="text-lg font-semibold text-center">
                {votesRevealed ? 'Votes Revealed' : 'Cast Your Vote'}
              </h3>
              <div className="grid grid-cols-5 sm:grid-cols-9 gap-3 justify-center">
                {voteOptions.map((value, index) => (
                  <VoteCard
                    key={value}
                    value={value}
                    isSelected={selectedVote === value}
                    disabled={votesRevealed || !room.current_story_data}
                    onClick={() => handleVote(value)}
                  />
                ))}
              </div>
            </div>
          </div>

          {/* Participants */}
          <div className="lg:col-span-3 space-y-4">
            <h2 className="text-lg font-semibold flex items-center gap-2 bg-gradient-to-r from-purple-600 to-indigo-600 bg-clip-text text-transparent">
              <Users className="w-5 h-5 text-purple-600" />
              Participants ({room.participants.filter(p => p.connected).length})
            </h2>
            
            <div className="space-y-3 max-h-[600px] overflow-y-auto pr-2">
              {room.participants.map((participant, index) => {
                const vote = room.current_story_data?.votes.find(
                  v => v.participant === participant.id
                );
                return (
                  <ParticipantCard
                    key={participant.id}
                    username={participant.username}
                    hasVoted={!!vote}
                    voteValue={vote?.value}
                    isRevealed={vote?.revealed || false}
                    connected={participant.connected}
                    index={index}
                  />
                );
              })}
            </div>

            {/* Leave Room Button */}
            <Button
              onClick={handleLeaveRoom}
              variant="outline"
              className="w-full border-red-500 text-red-500 hover:bg-red-50 dark:hover:bg-red-950"
              data-testid="leave-room-button"
            >
              <LogOut className="w-4 h-4 mr-2" />
              Leave Room
            </Button>
          </div>
        </div>

        {/* Dialogs */}
        <Dialog open={showAddStory} onOpenChange={setShowAddStory}>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Add New Story</DialogTitle>
              <DialogDescription>
                Add a new story to estimate. Leave fields empty for a randomly generated funny story!
              </DialogDescription>
            </DialogHeader>
            <div className="space-y-4">
              <div>
                <Label htmlFor="story-id">Story ID</Label>
                <Input
                  id="story-id"
                  value={newStory.story_id}
                  onChange={(e) => setNewStory({ ...newStory, story_id: e.target.value })}
                  placeholder="e.g., JIRA-123"
                  data-testid="story-id-input"
                />
              </div>
              <div>
                <Label htmlFor="story-title">Title</Label>
                <Input
                  id="story-title"
                  value={newStory.title}
                  onChange={(e) => setNewStory({ ...newStory, title: e.target.value })}
                  placeholder="e.g., User authentication"
                  data-testid="story-title-input"
                />
              </div>
            </div>
            <DialogFooter>
              <Button variant="outline" onClick={() => setShowAddStory(false)}>
                Cancel
              </Button>
              <Button 
                onClick={handleAddStory}
                className="bg-gradient-to-r from-purple-600 to-indigo-600"
                data-testid="add-story-submit"
              >
                Add Story
              </Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>

        <AlertDialog open={showResetConfirm} onOpenChange={setShowResetConfirm}>
          <AlertDialogContent>
            <AlertDialogHeader>
              <AlertDialogTitle>Reset All Votes?</AlertDialogTitle>
              <AlertDialogDescription>
                This will clear all votes for the current story. Everyone will need to vote again.
              </AlertDialogDescription>
            </AlertDialogHeader>
            <AlertDialogFooter>
              <AlertDialogCancel>Cancel</AlertDialogCancel>
              <AlertDialogAction 
                onClick={handleConfirmReset}
                className="bg-red-500 hover:bg-red-600"
              >
                Reset All Votes
              </AlertDialogAction>
            </AlertDialogFooter>
          </AlertDialogContent>
        </AlertDialog>

        <Dialog open={showAverageModal} onOpenChange={setShowAverageModal}>
          <DialogContent className="sm:max-w-md">
            <DialogHeader>
              <DialogTitle>Average Calculation</DialogTitle>
              <DialogDescription>
                Review the calculated average and decide on final points
              </DialogDescription>
            </DialogHeader>
            <div className="space-y-4 py-4">
              <div className="text-center space-y-2">
                <p className="text-3xl font-bold text-purple-600">
                  {averageData?.average.toFixed(2)}
                </p>
                <p className="text-sm text-gray-600 dark:text-gray-400">
                  Rounded to
                </p>
                <p className="text-5xl font-bold bg-gradient-to-r from-purple-600 to-indigo-600 bg-clip-text text-transparent">
                  {averageData?.rounded}
                </p>
              </div>
            </div>
            <DialogFooter className="sm:justify-center gap-3">
              <Button
                variant="outline"
                onClick={() => {
                  setShowAverageModal(false);
                  handleConfirmReset();
                }}
              >
                <XCircle className="w-4 h-4 mr-2" />
                Re-vote
              </Button>
              <Button 
                onClick={() => handleConfirmPoints(averageData?.rounded || 0)}
                className="bg-gradient-to-r from-emerald-500 to-green-600"
              >
                <CheckCircle className="w-4 h-4 mr-2" />
                Confirm {averageData?.rounded} Points
              </Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>
      </motion.div>
    </div>
  );
}

export default RoomModern;