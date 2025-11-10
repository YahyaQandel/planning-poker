# Planning Poker - Project Context

## Project Overview
A real-time planning poker application for agile teams to estimate story points collaboratively. Built with Django backend and React frontend featuring a modern, gradient-rich UI design with purple/indigo theme.

## Original Requirements

### Reference Application
- Base functionality inspired by: https://free-planning-poker.com
- Core concept: Quick, no-signup story point estimation tool

### Tech Stack Decision
- **Backend**: Django + Django Channels (WebSocket support)
- **Frontend**: React + TypeScript + Vite
- **UI Library**: shadcn/ui (customized with purple/indigo theme)
- **Styling**: Tailwind CSS
- **Real-time**: WebSocket via Django Channels + Redis
- **Font**: Inter
- **Icons**: Lucide
- **Animations**: Framer Motion

### Design System
- **Modern UI Redesign**: Purple/indigo gradient theme throughout
- **Light mode only**: Removed dark mode for consistent experience
- **Glass-morphism effects**: Backdrop blur and transparency
- **Gradient accents**: Purple-600 to indigo-600 gradients
- **Border radius**: Rounded corners (rounded-xl, rounded-2xl)
- **Shadow effects**: Enhanced shadows with purple tints

## Implemented Features (Current State)

### 1. Session/Room Management ✅
- Create new estimation room with unique 6-character code
- Auto-generated funny stories when fields left empty
- Share room via URL with copy button
- Reset room with confirmation dialog
- Room persistence during active session
- Real-time participant tracking

### 2. User Management ✅
- Join session without signup (username only)
- Live participant list with:
  - Connection status indicators (green/red)
  - Vote status (checkmark when voted)
  - Revealed votes display
  - Avatar initials with gradient borders
- Username display in header
- Leave room functionality

### 3. Story Management ✅
- **Story fields**: Story ID + Title (both optional)
- **Auto-generated funny stories** when fields empty:
  - Random combinations of adjectives, nouns, and verbs
  - Examples: "WOW-316: The Caffeinated Penguin Explores Quantum Physics"
- **Story sidebar** showing:
  - All stories with visual states (green=estimated, blue ring=current, gray=pending)
  - Running total of story points
  - Click to switch between stories
  - Vote count per story
- Prevents duplicate story IDs
- Story persistence across sessions

### 4. Voting System ✅
- **Fibonacci sequence**: 1, 2, 3, 5, 8, 13, 21
- **Special cards**: ? (uncertain), ☕ (coffee break)
- Hidden voting until reveal
- Visual vote status indicators
- Manual reveal with button
- Auto-enable reveal when all voted
- Vote persistence when switching stories

### 5. Planning Poker Calculation Logic ✅
- **Smart estimation algorithm**:
  - Detects wide spreads (>2 Fibonacci steps)
  - Uses 75th percentile for disagreements
  - Uses median for consensus
  - Always rounds to Fibonacci numbers
- **Discussion suggestions**:
  - Identifies participants with min/max votes
  - Shows personalized message: "Alice (voted 1) and Charlie (voted 21) should discuss"
  - Orange warning banner for wide spreads
- **Average display modal**:
  - Shows mathematical average
  - Shows recommended Fibonacci value
  - Re-vote and Confirm options

### 6. Real-time Updates ✅
- WebSocket connection for all features
- Live updates for:
  - Participant joins/leaves
  - Vote casting
  - Vote reveals
  - Story changes
  - Room resets
  - Points confirmation
- Automatic reconnection handling

### 7. Modern UI/UX Design ✅
- **Header Bar**:
  - Purple gradient background
  - Session name with sprint tag
  - Room code with copy button
  - Stats cards (Total Points, Stories, Progress)
  - Current date and participant count
  - Current username display
- **Voting Cards**:
  - Gradient hover effects
  - Selected state with purple gradient
  - Disabled state styling
  - Coffee emoji for break card
- **Participant Cards**:
  - Avatar with gradient text initials
  - White background with purple border
  - Enhanced shadow effects
  - Connection status badge
- **Responsive Design**:
  - Mobile-optimized grid layouts
  - Touch-friendly interactions
  - Collapsible sections

### 8. Additional Features ✅
- **Confirmation Dialogs**:
  - Reset confirmation with AlertDialog
  - Points confirmation after reveal
  - Existing story warning
- **Toast Notifications**:
  - Room code copied
  - Error messages
  - Success confirmations
- **Loading States**:
  - Room loading indicator
  - WebSocket connection status
- **Error Handling**:
  - Invalid room redirect
  - Connection loss handling
  - Form validation

## Technical Architecture

### Backend (Django)
```
backend/
├── config/              # Django settings, ASGI config
├── rooms/               # Main application
│   ├── models.py        # Room, Participant, Vote, Story
│   ├── consumers.py     # WebSocket handlers with Planning Poker logic
│   ├── serializers.py   # DRF serializers
│   ├── views.py         # REST API endpoints
│   └── routing.py       # WebSocket routing
└── requirements.txt
```

#### Key Models
- **Room**: code (unique), session_name, created_at, current_story (FK)
- **Participant**: room (FK), username, connected, session_id, joined_at
- **Story**: room (FK), story_id, title, final_points, estimated_at, order
- **Vote**: room (FK), participant (FK), story (FK), value, revealed, created_at

#### API Endpoints
- `POST /api/rooms/` - Create new room with optional story
- `GET /api/rooms/{code}/` - Get room details
- `POST /api/rooms/{code}/join/` - Join room with username
- `POST /api/rooms/{code}/reset/` - Reset current voting round
- `POST /api/rooms/{code}/reveal/` - Reveal all votes
- `POST /api/rooms/{code}/add_story/` - Add new story
- `POST /api/rooms/{code}/confirm_points/` - Confirm final points
- WebSocket: `/ws/room/{code}/` - Real-time communication

#### WebSocket Events
- `user_joined` - New participant joined
- `user_left` - Participant disconnected  
- `vote_cast` - User voted (value hidden)
- `votes_revealed` - All votes revealed with calculation
- `room_reset` - Votes cleared
- `story_added` - New story added
- `story_changed` - Current story switched
- `points_confirmed` - Final points saved
- `story_exists` - Duplicate story warning
- `discussion_message` - Wide spread discussion suggestion

#### Planning Poker Calculation
- `calculate_planning_poker_estimate()` - Smart Fibonacci rounding
- `get_discussion_suggestion()` - Generate discussion prompts
- `round_to_fibonacci()` - Always round up to Fibonacci

### Frontend (React)
```
frontend/
├── src/
│   ├── components/
│   │   ├── ui/              # shadcn components
│   │   ├── modern/          # Modern redesigned components
│   │   │   ├── HeaderBar.tsx     # Purple gradient header
│   │   │   ├── VoteCard.tsx      # Gradient voting cards
│   │   │   ├── ParticipantCard.tsx # Enhanced participant display
│   │   │   └── StoryCard.tsx     # Story state indicators
│   │   └── ThemeProvider.tsx # Light mode only
│   ├── pages/
│   │   ├── HomeModern.tsx   # Modern landing page
│   │   └── RoomModern.tsx   # Modern room interface
│   ├── hooks/
│   │   └── use-toast.ts     # Toast notifications
│   ├── lib/
│   │   ├── utils.ts         # shadcn utils
│   │   └── api.ts           # API client
│   └── styles/
│       └── globals.css      # Purple theme styles
├── components.json          # shadcn config
├── tailwind.config.ts       # Extended with animations
└── package.json
```

#### Key Components
- **HeaderBar**: Session info, stats, room code
- **VoteCard**: Individual voting option (1-21, ?, ☕)
- **ParticipantCard**: User display with vote status
- **StoryCard**: Story item with visual states
- **Dialog/AlertDialog**: Modals and confirmations

## Design Decisions

### Why Remove Dark Mode?
- Consistent visual experience
- Better contrast with purple gradients
- Simplified theme management
- Focus on single polished theme

### Why Purple/Indigo Theme?
- Modern, professional appearance
- Good contrast and accessibility
- Distinctive from typical blue themes
- Energetic and engaging

### Why Planning Poker Algorithm?
- Follows industry best practices
- Encourages discussion on disagreements
- Prevents underestimation bias
- Uses 75th percentile for wide spreads

### Why Funny Story Generator?
- Makes planning sessions more enjoyable
- Useful for demos and testing
- Reduces friction for quick starts
- Memorable story identifiers

## Current Status
- **Phase**: Production Ready
- **Completed Features**:
  ✅ Full voting flow
  ✅ Story management
  ✅ Real-time updates
  ✅ Planning Poker calculations
  ✅ Discussion suggestions
  ✅ Modern UI redesign
  ✅ Responsive design
  ✅ Error handling
  ✅ All core features implemented

## Recent Updates

### UI/UX Improvements
- Removed dark mode for consistency
- Enhanced purple gradient theme throughout
- Fixed text visibility issues (purple instead of white text)
- Added shadow effects and ring highlights
- Improved participant avatar styling
- Added username display in header

### Calculation Logic Updates
- Implemented proper Planning Poker estimation
- Added wide spread detection
- 75th percentile for disagreements
- Median for consensus
- Always rounds to Fibonacci sequence

### Discussion Features
- Automatic discussion suggestions
- Identifies participants to discuss
- Orange warning banner in modal
- Encourages re-voting after discussion

### Bug Fixes
- Fixed modal close handling (X button/escape key)
- Fixed state cleanup on modal dismiss
- Improved WebSocket reconnection
- Better error handling throughout

## Testing & Quality
- Comprehensive test files for calculations
- WebSocket event testing
- UI component testing
- Cross-browser compatibility
- Mobile responsiveness verified

## Deployment Ready
- Environment variables configured
- Production settings ready
- Static files optimized
- WebSocket configuration for production
- Redis configuration documented

## Documentation
- Comprehensive README with screenshots
- API documentation
- WebSocket event documentation
- Component documentation
- Setup instructions

## Future Enhancements (v2+)

### Potential Features
- Jira/GitHub integration
- Custom voting scales
- Session history/export
- Team workspaces
- Advanced analytics
- Spectator mode
- Sound notifications
- Persistent settings
- Velocity tracking
- Sprint retrospectives

## Questions Resolved
1. **Dark mode?** Removed for consistency ✓
2. **Calculation method?** Planning Poker best practices ✓
3. **Wide spreads?** Discussion suggestions implemented ✓
4. **UI theme?** Purple/indigo gradients ✓
5. **Story generation?** Funny auto-generator added ✓
6. **Modal issues?** Fixed close handling ✓

## Key Files Updated
- `backend/rooms/consumers.py` - Planning Poker logic
- `backend/rooms/views.py` - API endpoints
- `frontend/src/pages/RoomModern.tsx` - Main room interface
- `frontend/src/pages/HomeModern.tsx` - Landing page
- `frontend/src/components/modern/*` - All UI components
- `frontend/src/components/ThemeProvider.tsx` - Light mode only
- `README.md` - Complete documentation with images

## Success Metrics
- ✅ Real-time voting works flawlessly
- ✅ Planning Poker calculations accurate
- ✅ UI is modern and engaging
- ✅ No dark mode issues
- ✅ Discussion prompts helpful
- ✅ Story management intuitive
- ✅ Mobile responsive
- ✅ Production ready