import type { Story } from '@/types/index';
import { Card, CardContent } from '@/components/ui/card';

interface CurrentStoryProps {
  story: Story | null;
}

export default function CurrentStory({ story }: CurrentStoryProps) {
  if (!story) {
    return (
      <Card className="mb-6" data-testid="no-current-story">
        <CardContent className="p-6 text-center text-muted-foreground" data-testid="no-story-message">
          No story selected. Add a story to start estimating.
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className="mb-6" data-testid="current-story">
      <CardContent className="p-6">
        <div className="space-y-2">
          <div className="text-sm text-muted-foreground" data-testid="estimating-label">Currently Estimating</div>
          {story.story_id && (
            <div className="text-lg font-mono font-semibold text-primary" data-testid="current-story-id">
              {story.story_id}
            </div>
          )}
          {story.title && (
            <div className="text-xl font-semibold" data-testid="current-story-title">{story.title}</div>
          )}
          {!story.story_id && !story.title && (
            <div className="text-xl font-semibold text-muted-foreground" data-testid="untitled-story">Untitled Story</div>
          )}
        </div>
      </CardContent>
    </Card>
  );
}
