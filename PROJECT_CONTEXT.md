# Planning Poker - Project Context

## Project Overview
A real-time planning poker application for agile teams to estimate story points collaboratively. Built with Django backend and React frontend using the company's shadcn/ui design system.

## Original Requirements

### Reference Application
- Base functionality inspired by: https://free-planning-poker.com
- Core concept: Quick, no-signup story point estimation tool

### Tech Stack Decision
- **Backend**: Django + Django Channels (WebSocket support)
- **Frontend**: React + TypeScript + Vite
- **UI Library**: shadcn/ui (New York style, Zinc base color)
- **Styling**: Tailwind CSS
- **Real-time**: WebSocket via Django Channels + Redis
- **Font**: Inter
- **Icons**: Lucide

### Design System
- Using company's existing shadcn configuration from `/Users/yahya/projects/teracloud/webbi/webbi-frontend`
- Theme: New York style with Zinc color palette
- Full dark mode support
- Border radius: 0.5rem

## Feature Requirements

### Version 1 (MVP - Current Phase)

#### 1. Session/Room Management
- Create new estimation room with unique code
- Share room via URL (copy link functionality)
- Reset room to clear all votes and start new estimation round
- Room persistence during active session

#### 2. User Management
- Join session without signup/registration (just username)
- Set/change username
- Live participant list
- Connection status indicator
- **Note**: Kicking functionality deferred to v2 for easier tracing

#### 3. Story Management (Key Feature)
- **Story ID + Title fields** (both optional, manual input in v1)
- Display current story being estimated (ID + Title)
- **"Estimate New Story" button** to add another story
- **Left sidebar** showing:
  - List of all estimated stories
  - Each story shows: ID (if provided) + Title (if provided) + Final Points
  - **Running total** at the bottom
- Story information in URL parameter (e.g., `/room/abc123?story=JIRA-456`)

#### 4. Voting System
- Voting scale: Fibonacci sequence (0, 1, 2, 3, 5, 8, 13, 21, ?, ☕)
- Anonymous/hidden voting (votes hidden until reveal)
- Show who has voted (without revealing their vote)
- Manual reveal option
- Auto-reveal when everyone has voted

#### 5. Real-time Updates
- WebSocket connection for all real-time features
- Live participant list updates
- Vote status updates (who voted)
- Instant vote reveal synchronization
- Story list updates

#### 6. Basic UI/UX
- Clean, minimal interface
- Responsive design
- Share room URL with copy button
- Clear visual feedback for voting status

### Version 2 (Planned)

#### 1. User Management Enhancements
- **Kick user functionality** (anyone can kick any participant)
- Use cases: idle users, lost connectivity, moderation
- Idle/disconnect auto-detection
- **Spectator mode** (observers who don't vote)

#### 2. Story Integration
- Jira API integration (fetch story details automatically)
- Possible GitHub Issues integration
- Auto-populate story title from ID

#### 3. User Preferences
- Sound notifications toggle
- Browser notifications toggle
- Persistent user settings

#### 4. Basic Analytics
- Participation tracking
- Average estimates per story
- Voting efficiency metrics

### Version 3+ (Future Considerations)

#### Potential Features
- Historical data and trends
- Custom voting scales (not just Fibonacci)
- Advanced story/task management
- Team management
- Session history
- Export results

## Technical Architecture

### Backend (Django)
```
backend/
├── config/              # Django settings, ASGI config
├── rooms/               # Main application
│   ├── models.py        # Room, Participant, Vote, Story
│   ├── consumers.py     # WebSocket handlers
│   ├── serializers.py   # DRF serializers
│   ├── views.py         # REST API endpoints
│   └── routing.py       # WebSocket routing
└── requirements.txt
```

#### Key Models
- **Room**: code (unique), created_at, current_story_id
- **Participant**: room (FK), username, connected, session_id
- **Story**: room (FK), story_id (optional), title (optional), final_points, estimated_at, order
- **Vote**: room (FK), participant (FK), story (FK), value, revealed, created_at

#### API Endpoints
- `POST /api/rooms/` - Create new room
- `GET /api/rooms/{code}/` - Get room details
- `POST /api/rooms/{code}/join/` - Join room with username
- `POST /api/rooms/{code}/reset/` - Reset current voting round
- `POST /api/rooms/{code}/stories/` - Add new story to estimate
- WebSocket: `/ws/room/{code}/` - Real-time communication

#### WebSocket Events
- `user_joined` - New participant joined
- `user_left` - Participant disconnected
- `vote_cast` - User voted (don't reveal value)
- `votes_revealed` - All votes revealed
- `room_reset` - Votes cleared for new round
- `story_added` - New story added to list
- `story_changed` - Current story being estimated changed

### Frontend (React)

```
frontend/
├── src/
│   ├── components/
│   │   ├── ui/              # shadcn components (Button, Card, etc.)
│   │   ├── VotingCard.tsx   # Individual voting card
│   │   ├── VotingPanel.tsx  # Main voting interface
│   │   ├── ParticipantList.tsx  # User list with status
│   │   ├── StorySidebar.tsx     # Left sidebar with story list
│   │   ├── StoryTotal.tsx       # Running total component
│   │   ├── RoomControls.tsx     # Reset, reveal, add story buttons
│   │   └── CurrentStory.tsx     # Display current story info
│   ├── pages/
│   │   ├── Home.tsx         # Landing/create room
│   │   ├── Room.tsx         # Main room page
│   │   └── Join.tsx         # Join room page
│   ├── hooks/
│   │   ├── useWebSocket.ts  # WebSocket connection hook
│   │   └── useRoom.ts       # Room state management
│   ├── lib/
│   │   ├── utils.ts         # shadcn utils
│   │   └── api.ts           # API client
│   ├── types/
│   │   └── index.ts         # TypeScript types
│   └── styles.css           # Company theme (from webbi-frontend)
├── components.json          # shadcn config
├── tailwind.config.ts
└── package.json
```

#### Key Components
- **VotingPanel**: Main interface with voting cards (0, 1, 2, 3, 5, 8, 13, 21, ?, ☕)
- **ParticipantList**: Shows all users with voting status
- **StorySidebar**: Left panel with estimated stories list + total
- **CurrentStory**: Displays story being estimated (ID + Title)
- **RoomControls**: Reveal, Reset, Add Story, Share buttons

## Design Decisions

### Why Django + React?
- Django: Robust backend, excellent WebSocket support via Channels
- React: Better UX for real-time interactions, company standard
- Separation allows independent scaling

### Why Manual Story Input in v1?
- Faster initial development
- No external API dependencies
- Flexibility for any story tracking system
- Both fields optional for maximum flexibility

### Why Anyone Can Kick in v2?
- Democratic moderation
- Handles disconnected users quickly
- Simple implementation
- Deferred to v2 to focus on core voting flow first

### Why Left Sidebar for Story List?
- Always visible reference
- Running total readily available
- Historical context during estimation
- Doesn't interfere with main voting area

## Current Status
- **Phase**: Planning completed
- **Next Steps**: Start implementation
  1. Django project setup with Channels
  2. React project setup with shadcn theme
  3. Core models and WebSocket infrastructure
  4. Basic voting flow
  5. Story management sidebar

## Key Contacts & Resources
- Design System Source: `/Users/yahya/projects/teracloud/webbi/webbi-frontend`
- Reference App: https://free-planning-poker.com
- Company standard: shadcn/ui components

## Important Notes
- No user authentication/registration required
- Privacy-focused (following reference app principles)
- Real-time is core requirement (not polling)
- Story ID and Title are both optional fields
- Must match company design system exactly
- Dark mode support required

## Questions Resolved
1. **Tech stack?** Django + React ✓
2. **Who can kick users?** Anyone (v2 feature) ✓
3. **All features in v1?** No, phased approach ✓
4. **Story source?** Manual input (v1), API integration (v2+) ✓
5. **Story fields?** Both ID and Title optional ✓
6. **Design system?** Company's shadcn config ✓

## Future Considerations
- Jira API integration for auto-fetching story details
- GitHub Issues integration
- Custom voting scales
- Advanced analytics
- Session persistence/history
- Team workspaces
