import { FileText } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import type { Story } from '@/types/index';

interface StorySidebarProps {
  stories: Story[];
  currentStoryId?: string | null;
  onStoryClick?: (storyId: string) => void;
}

export default function StorySidebar({ stories, currentStoryId, onStoryClick }: StorySidebarProps) {
  const estimatedStories = stories.filter(s => s.final_points);

  const total = estimatedStories.reduce((sum, story) => {
    const points = story.final_points;
    if (points && points !== '?' && points !== 'coffee') {
      return sum + parseInt(points);
    }
    return sum;
  }, 0);

  return (
    <Card className="h-full">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <FileText className="w-5 h-5" />
          Stories ({stories.length})
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-3">
          {stories.length === 0 ? (
            <p className="text-sm text-muted-foreground">No stories added yet</p>
          ) : (
            <>
              {/* All Stories */}
              <div className="space-y-2">
                {stories.map((story) => (
                  <div
                    key={story.id}
                    className={`p-3 rounded-lg cursor-pointer transition-colors space-y-1 ${
                      story.id === currentStoryId
                        ? 'bg-primary text-primary-foreground'
                        : story.final_points
                        ? 'bg-green-50 border border-green-200 hover:bg-green-100'
                        : 'bg-muted hover:bg-muted/80'
                    }`}
                    onClick={() => onStoryClick?.(story.id)}
                  >
                    {story.story_id && (
                      <div className={`text-xs font-mono ${
                        story.id === currentStoryId ? 'text-primary-foreground/80' : 'text-muted-foreground'
                      }`}>
                        {story.story_id}
                      </div>
                    )}
                    {story.title && (
                      <div className="text-sm font-medium">{story.title}</div>
                    )}
                    {!story.story_id && !story.title && (
                      <div className={`text-sm ${
                        story.id === currentStoryId ? 'text-primary-foreground/80' : 'text-muted-foreground'
                      }`}>
                        Untitled Story
                      </div>
                    )}
                    <div className="flex items-center justify-between">
                      <span className={`text-xs ${
                        story.id === currentStoryId ? 'text-primary-foreground/80' : 'text-muted-foreground'
                      }`}>
                        {story.final_points ? 'Points:' : 'Not estimated'}
                      </span>
                      {story.final_points && (
                        <span className="font-bold text-lg">
                          {story.final_points === 'coffee' ? '☕' : story.final_points}
                        </span>
                      )}
                      {story.id === currentStoryId && !story.final_points && (
                        <span className="text-sm font-medium">← Current</span>
                      )}
                    </div>
                  </div>
                ))}
              </div>

              {/* Total Section */}
              {estimatedStories.length > 0 && (
                <div className="pt-3 border-t">
                  <div className="flex items-center justify-between p-3 rounded-lg bg-primary text-primary-foreground">
                    <span className="font-semibold">Total ({estimatedStories.length} estimated)</span>
                    <span className="font-bold text-2xl">{total}</span>
                  </div>
                </div>
              )}
            </>
          )}
        </div>
      </CardContent>
    </Card>
  );
}
