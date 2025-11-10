import { FileText } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import type { Story } from '@/types/index';

interface StorySidebarProps {
  stories: Story[];
}

export default function StorySidebar({ stories }: StorySidebarProps) {
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
          Estimated Stories
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-3">
          {estimatedStories.length === 0 ? (
            <p className="text-sm text-muted-foreground">No stories estimated yet</p>
          ) : (
            <>
              {estimatedStories.map((story) => (
                <div
                  key={story.id}
                  className="p-3 rounded-lg bg-muted space-y-1"
                >
                  {story.story_id && (
                    <div className="text-xs font-mono text-muted-foreground">
                      {story.story_id}
                    </div>
                  )}
                  {story.title && (
                    <div className="text-sm font-medium">{story.title}</div>
                  )}
                  {!story.story_id && !story.title && (
                    <div className="text-sm text-muted-foreground">Untitled Story</div>
                  )}
                  <div className="flex items-center justify-between">
                    <span className="text-xs text-muted-foreground">Points:</span>
                    <span className="font-bold text-lg">
                      {story.final_points === 'coffee' ? '☕' : story.final_points}
                    </span>
                  </div>
                </div>
              ))}

              <div className="pt-3 border-t">
                <div className="flex items-center justify-between p-3 rounded-lg bg-primary text-primary-foreground">
                  <span className="font-semibold">Total</span>
                  <span className="font-bold text-2xl">{total}</span>
                </div>
              </div>
            </>
          )}
        </div>
      </CardContent>
    </Card>
  );
}
