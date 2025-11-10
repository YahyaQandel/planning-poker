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
    <Card className="mt-4">
      <CardContent className="p-4">
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <div className="text-sm text-muted-foreground">Average:</div>
              <div className="text-2xl font-bold">{average.toFixed(2)}</div>
            </div>
            <div className="text-3xl font-bold text-muted-foreground">→</div>
            <div>
              <div className="text-sm text-muted-foreground">Rounded:</div>
              <div className="text-2xl font-bold">{rounded}</div>
            </div>
          </div>

          <div className="flex gap-2">
            <Button
              className="flex-1"
              variant="outline"
              onClick={onReject}
            >
              Re-vote
            </Button>
            <Button
              className="flex-1"
              onClick={onConfirm}
            >
              Confirm
            </Button>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
