import React from 'react';
import { motion } from 'framer-motion';
import { CheckCircle2, Circle, Clock, Hash } from 'lucide-react';
import { cn } from '@/lib/utils';

interface StoryCardProps {
  storyId: string;
  title: string;
  finalPoints?: string;
  votesCount: number;
  isCurrentStory: boolean;
  onClick: () => void;
}

const StoryCard: React.FC<StoryCardProps> = ({
  storyId,
  title,
  finalPoints,
  votesCount,
  isCurrentStory,
  onClick,
}) => {
  const isEstimated = !!finalPoints;
  const isPending = !isEstimated && !isCurrentStory;

  const getStatusIcon = () => {
    if (isEstimated) return <CheckCircle2 className="w-5 h-5 text-emerald-500" />;
    if (isCurrentStory) return <Clock className="w-5 h-5 text-purple-500 animate-pulse-slow" />;
    return <Circle className="w-5 h-5 text-gray-400" />;
  };

  const getCardBackground = () => {
    if (isCurrentStory) return 'bg-gradient-to-br from-purple-500/20 to-indigo-500/20 border-purple-500/50';
    if (isEstimated) return 'bg-gradient-to-br from-emerald-500/10 to-green-500/10 border-emerald-500/30';
    return 'bg-gradient-to-br from-white via-purple-50/30 to-white border-purple-200/60';
  };

  return (
    <motion.div
      whileHover={{ scale: 1.02 }}
      whileTap={{ scale: 0.98 }}
      initial={{ opacity: 0, x: -20 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ duration: 0.3 }}
      onClick={onClick}
      data-testid={`story-card-${storyId}`}
      className={cn(
        "relative p-4 rounded-xl border-2 cursor-pointer transition-all duration-300",
        "backdrop-blur-sm shadow-lg hover:shadow-xl",
        getCardBackground(),
        isCurrentStory && "ring-2 ring-purple-500 ring-offset-2 ring-offset-background"
      )}
    >
      {isCurrentStory && (
        <div className="absolute -top-2 -right-2">
          <span className="px-2 py-1 text-xs font-semibold text-white bg-gradient-to-r from-purple-600 to-indigo-600 rounded-full shadow-glow-sm">
            Active
          </span>
        </div>
      )}

      <div className="flex items-start justify-between gap-3">
        <div className="flex-1 space-y-1">
          <div className="flex items-center gap-2">
            {getStatusIcon()}
            <span className="text-sm font-medium text-purple-700 flex items-center gap-1">
              <Hash className="w-3 h-3" />
              {storyId}
            </span>
          </div>
          <h3 className={cn(
            "font-semibold line-clamp-2",
            isCurrentStory && "text-purple-800",
            isEstimated && "text-green-800",
            isPending && "text-purple-700"
          )}>
            {title}
          </h3>
          {votesCount > 0 && !isEstimated && (
            <p className="text-xs text-purple-600">
              {votesCount} vote{votesCount !== 1 ? 's' : ''} cast
            </p>
          )}
        </div>

        {finalPoints && (
          <motion.div
            initial={{ scale: 0 }}
            animate={{ scale: 1 }}
            transition={{ type: "spring", stiffness: 260, damping: 20 }}
            className="flex items-center justify-center w-12 h-12 rounded-lg bg-gradient-to-br from-emerald-500 to-green-600 text-white font-bold text-lg shadow-lg"
          >
            {finalPoints}
          </motion.div>
        )}
      </div>
    </motion.div>
  );
};

export default StoryCard;