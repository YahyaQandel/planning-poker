# Planning Poker Application

A real-time planning poker application for agile teams to estimate story points collaboratively. Built with Django backend and React frontend using shadcn/ui design system.

## 🏗️ Project Structure

```
planning-poker/
├── backend/                 # Django + Channels backend
│   ├── config/             # Django project settings
│   ├── rooms/              # Main application
│   │   ├── models.py       # Room, Participant, Vote, Story models
│   │   ├── consumers.py    # WebSocket handlers
│   │   ├── serializers.py  # DRF serializers
│   │   ├── views.py        # REST API endpoints
│   │   └── routing.py      # WebSocket routing
│   ├── manage.py
│   └── requirements.txt
│
├── frontend/               # React + TypeScript + Vite
│   ├── src/
│   │   ├── components/
│   │   │   └── ui/        # shadcn components
│   │   ├── lib/
│   │   │   └── utils.ts   # Utility functions
│   │   ├── hooks/         # Custom React hooks
│   │   ├── pages/         # Page components
│   │   ├── types/         # TypeScript types
│   │   └── index.css      # Company theme (Zinc/New York style)
│   ├── components.json     # shadcn config
│   └── package.json
│
└── PROJECT_CONTEXT.md      # Complete project documentation
```

## 🚀 Tech Stack

### Backend
- **Django 5.0** - Web framework
- **Django REST Framework** - API framework
- **Django Channels 4.0** - WebSocket support
- **Redis** - Channel layer backend
- **SQLite** - Database (dev)

### Frontend
- **React 18** - UI library
- **TypeScript** - Type safety
- **Vite** - Build tool
- **shadcn/ui** - Component library (New York style)
- **Tailwind CSS** - Styling
- **Lucide React** - Icons

## ✨ Features Implemented (v1)

### Backend
✅ Django models:
  - `Room` - Unique room codes, current story tracking
  - `Participant` - User management with session IDs
  - `Story` - Story tracking with optional ID/title
  - `Vote` - Vote management with reveal status

✅ REST API endpoints:
  - `POST /api/rooms/` - Create new room
  - `GET /api/rooms/{code}/` - Get room details
  - `POST /api/rooms/{code}/join/` - Join room
  - `POST /api/rooms/{code}/add_story/` - Add story
  - `POST /api/rooms/{code}/reset/` - Reset votes
  - `POST /api/rooms/{code}/reveal/` - Reveal votes

✅ WebSocket support:
  - Real-time vote casting
  - Live participant updates
  - Vote reveal synchronization
  - Story management events

### Frontend
✅ Project setup:
  - Vite + React + TypeScript
  - Tailwind CSS configured
  - shadcn/ui integration with company theme (Zinc/New York)
  - Path aliases (@/* imports)
  - Inter font family

## 📋 Setup Instructions

### Prerequisites
- Python 3.10+
- Node.js 18+ (Node 20+ recommended)
- Redis server

### Backend Setup

1. Navigate to backend directory:
```bash
cd backend
```

2. Create and activate virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Run migrations:
```bash
python manage.py migrate
```

5. Start Redis (required for WebSocket):
```bash
redis-server
```

6. Run development server:
```bash
python manage.py runserver
```

Backend will be available at `http://localhost:8000`

### Frontend Setup

1. Navigate to frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Start development server:
```bash
npm run dev
```

Frontend will be available at `http://localhost:5173`

## 🔌 API Endpoints

### REST API

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/rooms/` | Create new room |
| GET | `/api/rooms/{code}/` | Get room details |
| POST | `/api/rooms/{code}/join/` | Join room with username |
| POST | `/api/rooms/{code}/add_story/` | Add new story |
| POST | `/api/rooms/{code}/reset/` | Reset current votes |
| POST | `/api/rooms/{code}/reveal/` | Reveal all votes |

### WebSocket

Connect to: `ws://localhost:8000/ws/room/{room_code}/`

**Events:**
- `vote` - Cast a vote
- `reveal` - Reveal votes
- `reset` - Reset room
- `add_story` - Add new story
- `change_story` - Change current story
- `user_joined` - User joined notification
- `user_left` - User left notification

## 🎯 Next Steps

### Immediate (Complete v1)
- [ ] Create React components:
  - VotingCard
  - ParticipantList
  - StorySidebar
  - RoomControls
  - CurrentStory
- [ ] Implement pages:
  - Home/Create room
  - Join room
  - Room (main voting interface)
- [ ] Add WebSocket hook
- [ ] Connect API client
- [ ] Test end-to-end flow

### v2 Features
- [ ] Kick user functionality
- [ ] Spectator mode
- [ ] Idle/disconnect detection
- [ ] User preferences
- [ ] Basic analytics

### v3+ Features
- [ ] Jira API integration
- [ ] GitHub Issues integration
- [ ] Custom voting scales
- [ ] Advanced analytics
- [ ] Session history

## 📚 Documentation

See `PROJECT_CONTEXT.md` for complete project context, requirements, and design decisions.

## 🎨 Design System

This project uses your company's shadcn/ui configuration:
- **Style**: New York
- **Base Color**: Zinc
- **Font**: Inter
- **Radius**: 0.5rem
- **Icons**: Lucide
- **Dark Mode**: Fully supported

## 🔧 Development Notes

### Voting Scale
The application uses Fibonacci sequence:
- 0, 1, 2, 3, 5, 8, 13, 21, ?, ☕

### Story Fields
Both `story_id` and `title` are optional, allowing flexibility in usage.

### Real-time Communication
All real-time features use WebSocket via Django Channels with Redis as the channel layer.

## 📝 License

Internal project for Teracloud.

---

**Status**: Backend Complete ✅ | Frontend Setup Complete ✅ | UI Components Pending ⏳
