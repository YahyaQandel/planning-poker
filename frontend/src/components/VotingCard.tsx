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
  const displayValue = value === 'coffee' ? <Coffee className="w-8 h-8" /> : value;

  return (
    <Card
      className={cn(
        'cursor-pointer transition-all hover:scale-105 hover:shadow-lg flex items-center justify-center text-2xl font-bold h-24 w-20',
        selected && 'ring-4 ring-blue-500 bg-blue-500 text-white scale-110 shadow-xl border-blue-500',
        disabled && 'opacity-50 cursor-not-allowed hover:scale-100'
      )}
      style={selected ? {
        backgroundColor: '#3b82f6',
        color: 'white',
        borderColor: '#3b82f6',
        boxShadow: '0 0 0 4px rgba(59, 130, 246, 0.5)',
        transform: 'scale(1)'
      } : undefined}
      onClick={disabled ? undefined : onClick}
    >
      {displayValue}
    </Card>
  );
}
