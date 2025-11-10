import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Check, Clock, User, Wifi, WifiOff } from 'lucide-react';
import { cn } from '@/lib/utils';

interface ParticipantCardProps {
  username: string;
  hasVoted: boolean;
  voteValue?: string;
  isRevealed: boolean;
  connected: boolean;
  index: number;
}

const ParticipantCard: React.FC<ParticipantCardProps> = ({
  username,
  hasVoted,
  voteValue,
  isRevealed,
  connected,
  index,
}) => {
  const initials = username
    .split(' ')
    .map(word => word[0])
    .join('')
    .toUpperCase()
    .slice(0, 2);

  const avatarColors = [
    'from-purple-500 to-indigo-600',
    'from-indigo-500 to-blue-600',
    'from-blue-500 to-cyan-600',
    'from-emerald-500 to-green-600',
    'from-amber-500 to-orange-600',
    'from-pink-500 to-rose-600',
  ];

  const colorIndex = index % avatarColors.length;
  const avatarGradient = avatarColors[colorIndex];

  return (
    <motion.div
      initial={{ opacity: 0, x: 20 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ duration: 0.3, delay: index * 0.05 }}
      data-testid={`participant-${username}`}
      className={cn(
        "relative p-3 rounded-xl backdrop-blur-sm transition-all duration-300",
        "from-white via-purple-50/40 to-white dark:bg-gray-800/60 border",
        connected 
          ? "border-purple-200/60 dark:border-gray-700" 
          : "border-red-200 dark:border-red-900 opacity-60"
      )}
    >
      <div className="flex items-center gap-3">
        {/* Avatar */}
        <div className="relative">
          <div className={cn(
            "w-12 h-12 rounded-full flex items-center justify-center text-white font-bold",
            ` ${avatarGradient}`,
            "shadow-lg"
          )}>
            {initials}
          </div>
          
          {/* Connection Status */}
          <div className={cn(
            "absolute -bottom-1 -right-1 w-5 h-5 rounded-full flex items-center justify-center",
            connected ? "bg-emerald-500" : "bg-red-500",
            "border-2 border-white dark:border-gray-800"
          )}>
            {connected ? (
              <Wifi className="w-3 h-3 text-white" />
            ) : (
              <WifiOff className="w-3 h-3 text-white" />
            )}
          </div>
        </div>

        {/* User Info */}
        <div className="flex-1 min-w-0">
          <p className="font-medium text-white dark:text-gray-100 truncate">
            {username}
          </p>
          <div className="flex items-center gap-1 mt-0.5">
            {!hasVoted && connected && (
              <span className="text-xs text-white dark:text-gray-400 flex items-center gap-1">
                <Clock className="w-3 h-3" />
                Thinking...
              </span>
            )}
            {hasVoted && !isRevealed && (
              <span className="text-xs text-white dark:text-emerald-400 flex items-center gap-1">
                <Check className="w-3 h-3" />
                Voted
              </span>
            )}
            {!connected && (
              <span className="text-xs text-white dark:text-red-400">
                Disconnected
              </span>
            )}
          </div>
        </div>

        {/* Vote Display */}
        <AnimatePresence mode="wait">
          {hasVoted && (
            <motion.div
              initial={{ scale: 0, rotate: -180 }}
              animate={{ scale: 1, rotate: 0 }}
              exit={{ scale: 0, rotate: 180 }}
              transition={{ type: "spring", stiffness: 260, damping: 20 }}
              className={cn(
                "w-14 h-14 rounded-lg flex items-center justify-center font-bold text-lg",
                "shadow-lg transition-all duration-300"
              )}
            >
              {isRevealed && voteValue ? (
                <div className="bg-gradient-to-br from-purple-500 to-indigo-600 text-white w-full h-full rounded-lg flex items-center justify-center">
                  {voteValue === 'coffee' ? '☕' : voteValue}
                </div>
              ) : (
                <div className="bg-gradient-to-br from-gray-300 to-gray-400 dark:from-gray-600 dark:to-gray-700 text-white w-full h-full rounded-lg flex items-center justify-center">
                  <Check className="w-6 h-6" />
                </div>
              )}
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </motion.div>
  );
};

export default ParticipantCard;