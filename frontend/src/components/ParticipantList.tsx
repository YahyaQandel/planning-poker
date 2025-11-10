import { Users, Check } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import type { Participant, Vote } from '@/types/index';

interface ParticipantListProps {
  participants: Participant[];
  votes: Vote[];
  revealed: boolean;
}

export default function ParticipantList({ participants, votes, revealed }: ParticipantListProps) {
  const getVoteForParticipant = (participantId: string) => {
    return votes.find(v => v.participant === participantId);
  };

  return (
    <Card data-testid="participants-list">
      <CardHeader>
        <CardTitle className="flex items-center gap-2" data-testid="participants-header">
          <Users className="w-5 h-5" />
          Participants ({participants.filter(p => p.connected).length})
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-2" data-testid="participants-container">
          {participants.filter(p => p.connected).map((participant) => {
            const vote = getVoteForParticipant(participant.id);
            const hasVoted = !!vote;

            return (
              <div
                key={participant.id}
                className="flex items-center justify-between p-3 rounded-lg bg-muted"
                data-testid={`participant-${participant.id}`}
              >
                <span className="font-medium" data-testid={`participant-name-${participant.id}`}>{participant.username}</span>
                <div className="flex items-center gap-2">
                  {hasVoted && !revealed && (
                    <Check className="w-4 h-4 text-green-600" data-testid={`participant-voted-${participant.id}`} />
                  )}
                  {revealed && vote && (
                    <span className="px-2 py-1 bg-primary text-primary-foreground rounded font-bold" data-testid={`participant-vote-${participant.id}`}>
                      {vote.value === 'coffee' ? '☕' : vote.value}
                    </span>
                  )}
                  {!hasVoted && (
                    <span className="text-sm text-muted-foreground" data-testid={`participant-waiting-${participant.id}`}>Waiting...</span>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      </CardContent>
    </Card>
  );
}
