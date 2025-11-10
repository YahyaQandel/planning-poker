import React from 'react';
import { motion } from 'framer-motion';
import { 
  Calendar, 
  Copy, 
  Hash, 
  Moon, 
  Sun, 
  TrendingUp, 
  Users,
  Activity,
  Target
} from 'lucide-react';
import { cn } from '@/lib/utils';
import { useTheme } from '../ThemeProvider';

interface HeaderBarProps {
  sessionName: string;
  roomCode: string;
  totalPoints: number;
  estimatedStories: number;
  totalStories: number;
  participantsCount: number;
  onCopyCode: () => void;
}

const HeaderBar: React.FC<HeaderBarProps> = ({
  sessionName,
  roomCode,
  totalPoints,
  estimatedStories,
  totalStories,
  participantsCount,
  onCopyCode,
}) => {
  const { theme, setTheme } = useTheme();
  const progress = totalStories > 0 ? (estimatedStories / totalStories) * 100 : 0;

  const toggleTheme = () => {
    setTheme(theme === 'dark' ? 'light' : 'dark');
  };

  return (
    <motion.header
      initial={{ opacity: 0, y: -20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      className="relative overflow-hidden rounded-2xl bg-gradient-to-r from-purple-600 via-indigo-600 to-purple-700 p-6 shadow-2xl"
    >
      {/* Animated Background */}
      <div className="absolute inset-0 bg-gradient-to-r from-purple-600/20 via-transparent to-indigo-600/20 animate-gradient bg-[length:200%_200%]" />
      
      <div className="relative z-10">
        {/* Top Section */}
        <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4 mb-6">
          <div className="flex items-start gap-4">
            <img 
              src="/favicon.png" 
              alt="Planning Poker Logo" 
              className="w-16 h-16 lg:w-20 lg:h-20 rounded-xl bg-white/10 backdrop-blur-sm p-2"
            />
            <div>
              <h1 className="text-2xl lg:text-3xl font-bold text-white flex items-center gap-2">
                {sessionName}
                <span className="text-xs px-2 py-1 bg-white/20 rounded-full backdrop-blur-sm">
                  Sprint Planning
                </span>
              </h1>
              <div className="flex flex-wrap items-center gap-3 mt-2 text-white/80">
                <button
                  onClick={onCopyCode}
                  className="flex items-center gap-1 px-3 py-1 bg-white/10 rounded-lg hover:bg-white/20 transition-colors"
                  data-testid="copy-room-code"
                >
                  <Hash className="w-4 h-4" />
                  <span className="font-mono font-semibold">{roomCode}</span>
                  <Copy className="w-3 h-3" />
                </button>
                <div className="flex items-center gap-1">
                  <Calendar className="w-4 h-4" />
                  <span className="text-sm">{new Date().toLocaleDateString()}</span>
                </div>
                <div className="flex items-center gap-1">
                  <Users className="w-4 h-4" />
                  <span className="text-sm">{participantsCount} participants</span>
                </div>
              </div>
            </div>
          </div>

          {/* Theme Toggle */}
          <button
            onClick={toggleTheme}
            className="absolute top-4 right-4 lg:static p-2 rounded-lg bg-white/10 hover:bg-white/20 transition-colors"
            data-testid="theme-toggle"
          >
            {theme === 'dark' ? (
              <Sun className="w-5 h-5 text-white" />
            ) : (
              <Moon className="w-5 h-5 text-white" />
            )}
          </button>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-2 lg:grid-cols-3 gap-3">
          <motion.div
            whileHover={{ scale: 1.05 }}
            className="bg-white/10 backdrop-blur-sm rounded-xl p-3"
          >
            <div className="flex items-center gap-2 text-white/70 mb-1">
              <TrendingUp className="w-4 h-4" />
              <span className="text-xs font-medium">Total Points</span>
            </div>
            <p className="text-2xl font-bold text-white">{totalPoints}</p>
          </motion.div>

          <motion.div
            whileHover={{ scale: 1.05 }}
            className="bg-white/10 backdrop-blur-sm rounded-xl p-3"
          >
            <div className="flex items-center gap-2 text-white/70 mb-1">
              <Target className="w-4 h-4" />
              <span className="text-xs font-medium">Stories</span>
            </div>
            <p className="text-2xl font-bold text-white">
              {estimatedStories}/{totalStories}
            </p>
          </motion.div>


          <motion.div
            whileHover={{ scale: 1.05 }}
            className="bg-white/10 backdrop-blur-sm rounded-xl p-3"
          >
            <div className="flex items-center gap-2 text-white/70 mb-1">
              <Activity className="w-4 h-4" />
              <span className="text-xs font-medium">Progress</span>
            </div>
            <div className="mt-2">
              <div className="w-full bg-white/20 rounded-full h-2">
                <motion.div
                  initial={{ width: 0 }}
                  animate={{ width: `${progress}%` }}
                  transition={{ duration: 1, ease: "easeOut" }}
                  className="h-full bg-gradient-to-r from-emerald-400 to-green-500 rounded-full"
                />
              </div>
              <p className="text-xs text-white/70 mt-1">{Math.round(progress)}%</p>
            </div>
          </motion.div>
        </div>
      </div>
    </motion.header>
  );
};

export default HeaderBar;