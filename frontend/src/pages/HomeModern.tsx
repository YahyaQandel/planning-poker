import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { 
  Sparkles, 
  Users, 
  Hash, 
  Zap,
  ArrowRight,
  Shuffle,
  Moon,
  Sun
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { useToast } from '@/components/ui/use-toast';
import { useTheme } from '@/components/ThemeProvider';
import { cn } from '@/lib/utils';

function HomeModern() {
  const navigate = useNavigate();
  const { toast } = useToast();
  const { theme, setTheme } = useTheme();
  const [createForm, setCreateForm] = useState({
    username: '',
    story_id: '',
    title: ''
  });
  const [joinForm, setJoinForm] = useState({
    username: '',
    roomCode: ''
  });
  const [isCreating, setIsCreating] = useState(false);
  const [isJoining, setIsJoining] = useState(false);

  const generateSessionId = () => {
    return `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
  };

  const handleCreateRoom = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!createForm.username.trim()) {
      toast({
        title: "Username required",
        description: "Please enter your username to create a room",
        variant: "destructive",
      });
      return;
    }

    setIsCreating(true);
    try {
      // Create room
      const roomResponse = await fetch(`${import.meta.env.VITE_API_URL}/rooms/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          story_id: createForm.story_id,
          title: createForm.title
        })
      });

      if (!roomResponse.ok) throw new Error('Failed to create room');
      const roomData = await roomResponse.json();

      // Join room
      const sessionId = generateSessionId();
      const joinResponse = await fetch(`${import.meta.env.VITE_API_URL}/rooms/${roomData.code}/join/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          username: createForm.username,
          session_id: sessionId
        })
      });

      if (!joinResponse.ok) throw new Error('Failed to join room');
      const joinData = await joinResponse.json();

      // Store user info
      localStorage.setItem('participant_id', joinData.participant.id);
      localStorage.setItem('username', createForm.username);
      localStorage.setItem('session_id', sessionId);

      navigate(`/room/${roomData.code}`);
    } catch (error) {
      console.error('Error:', error);
      toast({
        title: "Error",
        description: "Failed to create room. Please try again.",
        variant: "destructive",
      });
    } finally {
      setIsCreating(false);
    }
  };

  const handleJoinRoom = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!joinForm.username.trim() || !joinForm.roomCode.trim()) {
      toast({
        title: "All fields required",
        description: "Please enter both username and room code",
        variant: "destructive",
      });
      return;
    }

    setIsJoining(true);
    try {
      const sessionId = generateSessionId();
      const response = await fetch(`${import.meta.env.VITE_API_URL}/rooms/${joinForm.roomCode}/join/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          username: joinForm.username,
          session_id: sessionId
        })
      });

      if (!response.ok) {
        if (response.status === 404) {
          throw new Error('Room not found');
        }
        throw new Error('Failed to join room');
      }

      const data = await response.json();

      // Store user info
      localStorage.setItem('participant_id', data.participant.id);
      localStorage.setItem('username', joinForm.username);
      localStorage.setItem('session_id', sessionId);

      navigate(`/room/${joinForm.roomCode}`);
    } catch (error: any) {
      console.error('Error:', error);
      toast({
        title: "Error",
        description: error.message || "Failed to join room. Please check the room code.",
        variant: "destructive",
      });
    } finally {
      setIsJoining(false);
    }
  };

  const toggleTheme = () => {
    setTheme(theme === 'dark' ? 'light' : 'dark');
  };

  return (
    <div className="min-h-screen flex items-center justify-center p-4">
      {/* Animated background elements */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-20 left-20 w-72 h-72 bg-purple-300 dark:bg-purple-900 rounded-full mix-blend-multiply dark:mix-blend-screen filter blur-3xl opacity-30 animate-pulse-slow" />
        <div className="absolute bottom-20 right-20 w-72 h-72 bg-indigo-300 dark:bg-indigo-900 rounded-full mix-blend-multiply dark:mix-blend-screen filter blur-3xl opacity-30 animate-pulse-slow animation-delay-2000" />
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-96 h-96 bg-pink-300 dark:bg-pink-900 rounded-full mix-blend-multiply dark:mix-blend-screen filter blur-3xl opacity-20 animate-pulse-slow animation-delay-4000" />
      </div>

      {/* Theme Toggle */}
      <button
        onClick={toggleTheme}
        className="fixed top-4 right-4 p-3 rounded-xl bg-white/80 dark:bg-gray-800/80 backdrop-blur-sm border border-gray-200 dark:border-gray-700 shadow-lg hover:shadow-xl transition-all"
        data-testid="theme-toggle"
      >
        {theme === 'dark' ? (
          <Sun className="w-5 h-5 text-amber-500" />
        ) : (
          <Moon className="w-5 h-5 text-indigo-600" />
        )}
      </button>

      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="w-full max-w-5xl relative z-10"
      >
        {/* Header */}
        <div className="text-center mb-8">
          <motion.div
            initial={{ scale: 0 }}
            animate={{ scale: 1 }}
            transition={{ type: "spring", stiffness: 260, damping: 20 }}
            className="inline-flex items-center justify-center gap-4 mb-6"
          >
            <div className="relative">
              <img 
                src="/favicon.png" 
                alt="Planning Poker Logo" 
                className="w-20 h-20 lg:w-24 lg:h-24 rounded-2xl shadow-2xl"
                data-testid="planning-poker-logo"
              />
              <div className="absolute -inset-1 bg-gradient-to-r from-purple-600 to-indigo-600 rounded-2xl blur opacity-30 animate-pulse-slow" />
            </div>
            <h1 className="text-5xl lg:text-6xl font-bold bg-gradient-to-r from-purple-600 via-indigo-600 to-purple-700 bg-clip-text text-transparent">
              Planning Poker
            </h1>
          </motion.div>
          
          <motion.p
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.2 }}
            className="text-lg text-gray-600 dark:text-gray-400 max-w-2xl mx-auto"
          >
            Collaborative story point estimation for agile teams. Create or join a room to start your sprint planning session.
          </motion.p>
        </div>

        {/* Feature Pills */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.3 }}
          className="flex flex-wrap justify-center gap-3 mb-8"
        >
          {[
            { icon: Zap, text: "Real-time Voting", color: "from-amber-500 to-orange-600" },
            { icon: Users, text: "Team Collaboration", color: "from-emerald-500 to-green-600" },
            { icon: Sparkles, text: "Auto-Generated Stories", color: "from-purple-500 to-indigo-600" },
            { icon: Shuffle, text: "Sprint Planning", color: "from-pink-500 to-rose-600" },
          ].map((feature, index) => (
            <motion.div
              key={index}
              whileHover={{ scale: 1.05 }}
              className={cn(
                "flex items-center gap-2 px-4 py-2 rounded-full",
                "bg-gradient-to-r text-white text-sm font-medium shadow-lg",
                feature.color
              )}
            >
              <feature.icon className="w-4 h-4" />
              {feature.text}
            </motion.div>
          ))}
        </motion.div>

        {/* Main Cards */}
        <Tabs defaultValue="create" className="w-full">
          <TabsList className="grid w-full max-w-md mx-auto grid-cols-2 mb-6">
            <TabsTrigger value="create" className="data-[state=active]:bg-gradient-to-r data-[state=active]:from-purple-600 data-[state=active]:to-indigo-600 data-[state=active]:text-white">
              Create Room
            </TabsTrigger>
            <TabsTrigger value="join" className="data-[state=active]:bg-gradient-to-r data-[state=active]:from-purple-600 data-[state=active]:to-indigo-600 data-[state=active]:text-white">
              Join Room
            </TabsTrigger>
          </TabsList>

          <TabsContent value="create">
            <Card className="backdrop-blur-sm bg-background/90 border-border shadow-2xl">
              <CardHeader>
                <CardTitle className="text-2xl bg-gradient-to-r from-purple-600 to-indigo-600 bg-clip-text text-transparent">
                  Create New Room
                </CardTitle>
                <CardDescription>
                  Start a new planning session for your team. Leave story fields empty for a fun surprise!
                </CardDescription>
              </CardHeader>
              <form onSubmit={handleCreateRoom}>
                <CardContent className="space-y-4">
                  <div className="space-y-2">
                    <Label htmlFor="create-username" className="text-sm font-medium">
                      Your Name *
                    </Label>
                    <Input
                      id="create-username"
                      value={createForm.username}
                      onChange={(e) => setCreateForm({ ...createForm, username: e.target.value })}
                      placeholder="Enter your name"
                      className="bg-input"
                      data-testid="create-username"
                      required
                    />
                  </div>
                  
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div className="space-y-2">
                      <Label htmlFor="story-id" className="text-sm font-medium flex items-center gap-2">
                        <Hash className="w-3 h-3" />
                        Story ID
                      </Label>
                      <Input
                        id="story-id"
                        value={createForm.story_id}
                        onChange={(e) => setCreateForm({ ...createForm, story_id: e.target.value })}
                        placeholder="e.g., JIRA-123"
                        className="bg-input"
                        data-testid="story-id"
                      />
                    </div>
                    
                    <div className="space-y-2">
                      <Label htmlFor="story-title" className="text-sm font-medium">
                        Story Title
                      </Label>
                      <Input
                        id="story-title"
                        value={createForm.title}
                        onChange={(e) => setCreateForm({ ...createForm, title: e.target.value })}
                        placeholder="e.g., User Authentication"
                        className="bg-input"
                        data-testid="story-title"
                      />
                    </div>
                  </div>
                  
                  <div className="p-4 bg-muted/50 rounded-lg">
                    <p className="text-sm text-purple-600 dark:text-purple-400 flex items-center gap-2">
                      <Sparkles className="w-4 h-4" />
                      Leave story fields empty for auto-generated funny stories!
                    </p>
                  </div>
                </CardContent>
                <CardFooter>
                  <Button 
                    type="submit"
                    disabled={isCreating}
                    className="w-full bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-700 hover:to-indigo-700 text-white shadow-lg hover:shadow-xl transition-all"
                    data-testid="create-room-button"
                  >
                    {isCreating ? (
                      <>Creating...</>
                    ) : (
                      <>
                        Create Room
                        <ArrowRight className="w-4 h-4 ml-2" />
                      </>
                    )}
                  </Button>
                </CardFooter>
              </form>
            </Card>
          </TabsContent>

          <TabsContent value="join">
            <Card className="backdrop-blur-sm bg-background/90 border-border shadow-2xl">
              <CardHeader>
                <CardTitle className="text-2xl bg-gradient-to-r from-purple-600 to-indigo-600 bg-clip-text text-transparent">
                  Join Existing Room
                </CardTitle>
                <CardDescription>
                  Enter the room code shared by your team to join the planning session
                </CardDescription>
              </CardHeader>
              <form onSubmit={handleJoinRoom}>
                <CardContent className="space-y-4">
                  <div className="space-y-2">
                    <Label htmlFor="join-username" className="text-sm font-medium">
                      Your Name *
                    </Label>
                    <Input
                      id="join-username"
                      value={joinForm.username}
                      onChange={(e) => setJoinForm({ ...joinForm, username: e.target.value })}
                      placeholder="Enter your name"
                      className="bg-input"
                      data-testid="join-username"
                      required
                    />
                  </div>
                  
                  <div className="space-y-2">
                    <Label htmlFor="room-code" className="text-sm font-medium flex items-center gap-2">
                      <Hash className="w-3 h-3" />
                      Room Code *
                    </Label>
                    <Input
                      id="room-code"
                      value={joinForm.roomCode}
                      onChange={(e) => setJoinForm({ ...joinForm, roomCode: e.target.value.toUpperCase() })}
                      placeholder="e.g., ABC123"
                      className="bg-white/50 dark:bg-gray-800/50 font-mono text-lg tracking-wider"
                      maxLength={6}
                      data-testid="room-code"
                      required
                    />
                  </div>
                </CardContent>
                <CardFooter>
                  <Button 
                    type="submit"
                    disabled={isJoining}
                    className="w-full bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-700 hover:to-indigo-700 text-white shadow-lg hover:shadow-xl transition-all"
                    data-testid="join-room-button"
                  >
                    {isJoining ? (
                      <>Joining...</>
                    ) : (
                      <>
                        Join Room
                        <Users className="w-4 h-4 ml-2" />
                      </>
                    )}
                  </Button>
                </CardFooter>
              </form>
            </Card>
          </TabsContent>
        </Tabs>
      </motion.div>
    </div>
  );
}

export default HomeModern;