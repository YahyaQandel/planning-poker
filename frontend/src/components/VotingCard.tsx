import { Coffee } from 'lucide-react';
import { Card } from '@/components/ui/card';
import { cn } from '@/lib/utils';
import type { VoteValue } from '@/types/index';

interface VotingCardProps {
  value: VoteValue;
  selected: boolean;
  onClick: () => void;
  disabled?: boolean;
}

export default function VotingCard({ value, selected, onClick, disabled }: VotingCardProps) {

  return (
    <Card
      className={cn(
        'cursor-pointer transition-all hover:scale-105 hover:shadow-lg flex items-center justify-center font-bold',
        'text-sm sm:text-lg lg:text-2xl',
        'h-12 w-12 sm:h-16 sm:w-16 lg:h-24 lg:w-20',
        selected && 'ring-2 sm:ring-4 ring-blue-500 bg-blue-500 text-white shadow-xl border-blue-500',
        disabled && 'opacity-50 cursor-not-allowed hover:scale-100'
      )}
      style={selected ? {
        backgroundColor: '#3b82f6',
        color: 'white',
        borderColor: '#3b82f6',
        boxShadow: '0 0 0 2px rgba(59, 130, 246, 0.5)',
        transform: 'scale(1)'
      } : undefined}
      onClick={disabled ? undefined : onClick}
      data-testid={`voting-card-${value}`}
    >
      <span className="flex items-center justify-center w-full h-full">
        {value === 'coffee' ? <Coffee className="w-4 h-4 sm:w-6 sm:h-6 lg:w-8 lg:h-8" /> : value}
      </span>
    </Card>
  );
}
