import React from 'react';
import { motion } from 'framer-motion';
import { Coffee, HelpCircle } from 'lucide-react';
import { cn } from '@/lib/utils';

interface VoteCardProps {
  value: string;
  isSelected: boolean;
  disabled: boolean;
  onClick: () => void;
}

const VoteCard: React.FC<VoteCardProps> = ({ 
  value, 
  isSelected, 
  disabled, 
  onClick 
}) => {
  const isSpecial = value === '?' || value === 'coffee';
  
  const getCardContent = () => {
    if (value === '?') return <HelpCircle className="w-8 h-8" />;
    if (value === 'coffee') return <Coffee className="w-8 h-8" />;
    return value;
  };

  const getCardGradient = () => {
    if (isSelected) {
      return isSpecial 
        ? 'from-orange-500 to-amber-600' 
        : 'from-purple-600 to-indigo-600';
    }
    return '';
  };

  return (
    <motion.button
      whileHover={!disabled ? { scale: 1.05, y: -5 } : {}}
      whileTap={!disabled ? { scale: 0.95 } : {}}
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      onClick={onClick}
      disabled={disabled}
      data-testid={`voting-card-${value}`}
      className={cn(
        "relative w-20 h-28 sm:w-24 sm:h-32 rounded-2xl font-bold text-2xl transition-all duration-300",
        "shadow-lg hover:shadow-2xl backdrop-blur-sm",
        "flex items-center justify-center",
        disabled && "opacity-50 cursor-not-allowed",
        !disabled && !isSelected && [
          "from-white via-purple-50/50 to-white dark:bg-gray-800/80 text-gray-700 dark:text-gray-300",
          "border-2 border-purple-200/60 dark:border-gray-700",
          "hover:bg-gradient-to-br hover:from-purple-50 hover:via-purple-100/50 hover:to-purple-50",
          "dark:hover:from-gray-800 dark:hover:to-gray-900"
        ],
        isSelected && [
          `bg-gradient-to-br ${getCardGradient()} text-white`,
          "border-2 border-transparent",
          "shadow-glow transform-gpu"
        ]
      )}
    >
      {isSelected && (
        <motion.div
          className="absolute inset-0 rounded-2xl bg-gradient-to-br from-white/20 to-transparent"
          initial={{ opacity: 0 }}
          animate={{ opacity: [0, 0.5, 0] }}
          transition={{ duration: 2, repeat: Infinity }}
        />
      )}
      
      <motion.div
        animate={isSelected ? { rotate: [0, -5, 5, -5, 0] } : {}}
        transition={{ duration: 0.5 }}
      >
        {getCardContent()}
      </motion.div>

      {!isSpecial && (
        <div className={cn(
          "absolute top-2 right-2 text-xs font-medium",
          isSelected ? "text-white/80" : "text-gray-500 dark:text-gray-400"
        )}>
          pts
        </div>
      )}
    </motion.button>
  );
};

export default VoteCard;