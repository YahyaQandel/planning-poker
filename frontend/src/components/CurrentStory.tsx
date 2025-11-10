import type { Story } from '@/types/index';
import { Card, CardContent } from '@/components/ui/card';

interface CurrentStoryProps {
  story: Story | null;
}

export default function CurrentStory({ story }: CurrentStoryProps) {
  if (!story) {
    return (
      <Card className="mb-6">
        <CardContent className="p-6 text-center text-muted-foreground">
          No story selected. Add a story to start estimating.
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className="mb-6">
      <CardContent className="p-6">
        <div className="space-y-2">
          <div className="text-sm text-muted-foreground">Currently Estimating</div>
          {story.story_id && (
            <div className="text-lg font-mono font-semibold text-primary">
              {story.story_id}
            </div>
          )}
          {story.title && (
            <div className="text-xl font-semibold">{story.title}</div>
          )}
          {!story.story_id && !story.title && (
            <div className="text-xl font-semibold text-muted-foreground">Untitled Story</div>
          )}
        </div>
      </CardContent>
    </Card>
  );
}
