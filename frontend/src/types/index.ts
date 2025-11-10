export interface Room {
  code: string;
  session_name: string;
  created_at: string;
  updated_at: string;
  current_story: string | null;
  current_story_data: Story | null;
  participants: Participant[];
  stories: Story[];
  participants_count: number;
}

export interface Participant {
  id: string;
  username: string;
  connected: boolean;
  joined_at: string;
  last_seen: string;
}

export interface Story {
  id: string;
  story_id: string | null;
  title: string | null;
  final_points: string | null;
  estimated_at: string | null;
  order: number;
  votes: Vote[];
  votes_count: number;
  created_at: string;
}

export interface Vote {
  id: string;
  participant: string;
  participant_name: string;
  value: string;
  revealed: boolean;
  created_at: string;
}

export type VoteValue = '0' | '1' | '2' | '3' | '5' | '8' | '13' | '21' | '?' | 'coffee';

export const VOTE_OPTIONS: VoteValue[] = ['0', '1', '2', '3', '5', '8', '13', '21', '?', 'coffee'];
