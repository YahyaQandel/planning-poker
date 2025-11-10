import { Button } from '@/components/ui/button';
import { X, TrendingUp, Target } from 'lucide-react';

interface ConfirmPointsDialogProps {
  average: number;
  rounded: number;
  onConfirm: () => void;
  onReject: () => void;
  onClose?: () => void;
}

export default function ConfirmPointsDialog({
  average,
  rounded,
  onConfirm,
  onReject,
  onClose
}: ConfirmPointsDialogProps) {
  return (
    <div className="mt-4 relative border-purple-300  from-white via-purple-50 to-purple-100 shadow-2xl backdrop-blur-lg border-2 rounded-3xl ring-1 ring-purple-200/50 overflow-hidden" data-testid="confirm-points-card">
      {onClose && (
        <Button
          variant="ghost"
          size="sm"
          className="absolute right-2 top-2 h-6 w-6 p-0 hover:bg-purple-100"
          onClick={onClose}
          data-testid="close-dialog-button"
        >
          <X className="h-4 w-4" />
        </Button>
      )}
      
      <div className="p-6 pb-3">
        <div className="flex items-center gap-2 text-lg text-purple-800 font-semibold">
          <Target className="w-5 h-5" />
          Finalize Story Points
        </div>
      </div>
      
      <div className="p-6 pt-0">
        <div className="space-y-6">
          <div className="flex items-center justify-center gap-6" data-testid="average-calculation">
            <div className="text-center">
              <div className="flex items-center gap-2 justify-center mb-2">
                <TrendingUp className="w-4 h-4 text-purple-600" />
                <span className="text-sm font-medium text-purple-700">Average</span>
              </div>
              <div className="text-3xl font-bold text-purple-800 bg-purple-100 rounded-lg px-4 py-2" data-testid="average-value">
                {average.toFixed(2)}
              </div>
            </div>
            
            <div className="text-4xl font-bold text-purple-400">→</div>
            
            <div className="text-center">
              <div className="flex items-center gap-2 justify-center mb-2">
                <Target className="w-4 h-4 text-indigo-600" />
                <span className="text-sm font-medium text-indigo-700">Final Points</span>
              </div>
              <div className="text-4xl font-bold text-indigo-800  from-indigo-100 to-purple-100 rounded-lg px-4 py-3 shadow-inner" data-testid="rounded-value">
                {rounded}
              </div>
            </div>
          </div>

          <div className="flex gap-3">
            <Button
              className="flex-1 bg-gray-100 hover:bg-gray-200 text-gray-700 border-gray-300"
              variant="outline"
              onClick={onReject}
              data-testid="reject-points-button"
            >
              <X className="w-4 h-4 mr-2" />
              Re-vote
            </Button>
            <Button
              className="flex-1 bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-700 hover:to-indigo-700 text-white shadow-lg"
              onClick={onConfirm}
              data-testid="confirm-points-button"
            >
              <Target className="w-4 h-4 mr-2" />
              Confirm Points
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
}
