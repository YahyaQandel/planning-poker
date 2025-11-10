import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';

interface ConfirmPointsDialogProps {
  average: number;
  rounded: number;
  onConfirm: () => void;
  onReject: () => void;
}

export default function ConfirmPointsDialog({
  average,
  rounded,
  onConfirm,
  onReject
}: ConfirmPointsDialogProps) {
  return (
    <Card className="mt-4" data-testid="confirm-points-card">
      <CardContent className="p-4">
        <div className="space-y-4">
          <div className="flex items-center justify-between" data-testid="average-calculation">
            <div>
              <div className="text-sm text-muted-foreground">Average:</div>
              <div className="text-2xl font-bold" data-testid="average-value">{average.toFixed(2)}</div>
            </div>
            <div className="text-3xl font-bold text-muted-foreground">→</div>
            <div>
              <div className="text-sm text-muted-foreground">Rounded:</div>
              <div className="text-2xl font-bold" data-testid="rounded-value">{rounded}</div>
            </div>
          </div>

          <div className="flex gap-2">
            <Button
              className="flex-1"
              variant="outline"
              onClick={onReject}
              data-testid="reject-points-button"
            >
              Re-vote
            </Button>
            <Button
              className="flex-1"
              onClick={onConfirm}
              data-testid="confirm-points-button"
            >
              Confirm
            </Button>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
