# Frontend Architecture Documentation

## Overview

The frontend is a NextJS 15+ application with TypeScript and Tailwind CSS, implementing a Kanban board project management application with AI chat capabilities.

## Technology Stack

### Core Frameworks

- **NextJS 15+**: React framework with App Router
- **TypeScript**: Type-safe JavaScript
- **Tailwind CSS**: Utility-first CSS framework
- **React 19**: Latest React version with concurrent features

### Key Libraries

- **@dnd-kit**: Drag and drop functionality for Kanban cards
- **axios**: HTTP client for API calls
- **jose**: JWT token handling
- **date-fns**: Date manipulation
- **react-hook-form**: Form handling
- **zod**: Schema validation
- **@tanstack/react-query**: Data fetching and caching
- **zustand**: State management (if needed beyond React Context)

### Testing

- **Jest**: Test runner
- **React Testing Library**: Component testing
- **Playwright**: E2E testing
- **MSW**: Mock Service Worker for API mocking

## Project Structure

```
frontend/
├── app/                    # NextJS App Router
│   ├── (auth)/            # Authentication routes
│   │   ├── login/
│   │   │   └── page.tsx
│   │   └── layout.tsx
│   ├── (dashboard)/       # Protected dashboard routes
│   │   ├── layout.tsx
│   │   └── page.tsx       # Main Kanban board
│   ├── api/               # API routes (if needed)
│   ├── layout.tsx         # Root layout
│   └── globals.css        # Global styles
├── components/            # Reusable components
│   ├── ui/               # Base UI components
│   │   ├── Button.tsx
│   │   ├── Card.tsx
│   │   ├── Input.tsx
│   │   └── Modal.tsx
│   ├── kanban/           # Kanban-specific components
│   │   ├── KanbanBoard.tsx
│   │   ├── KanbanColumn.tsx
│   │   ├── KanbanCard.tsx
│   │   └── CardEditor.tsx
│   ├── chat/             # AI chat components
│   │   ├── ChatSidebar.tsx
│   │   ├── ChatMessage.tsx
│   │   └── ChatInput.tsx
│   └── layout/           # Layout components
│       ├── Header.tsx
│       ├── Sidebar.tsx
│       └── Footer.tsx
├── lib/                  # Utility libraries
│   ├── api/              # API client
│   │   ├── client.ts
│   │   ├── auth.ts
│   │   ├── boards.ts
│   │   └── ai.ts
│   ├── hooks/            # Custom React hooks
│   │   ├── useAuth.ts
│   │   ├── useKanban.ts
│   │   └── useWebSocket.ts
│   ├── utils/            # Utility functions
│   │   ├── validation.ts
│   │   ├── formatting.ts
│   │   └── constants.ts
│   └── types/            # TypeScript types
│       ├── kanban.ts
│       ├── auth.ts
│       └── ai.ts
├── stores/               # State stores (if using zustand)
│   ├── auth.store.ts
│   └── kanban.store.ts
├── styles/               # Additional styles
│   ├── tailwind.config.ts
│   └── colors.ts         # Color scheme constants
├── tests/                # Test files
│   ├── unit/
│   ├── integration/
│   └── e2e/
└── public/               # Static assets
```

## Color Scheme Implementation

The color scheme will be implemented as Tailwind CSS custom colors:

```typescript
// styles/colors.ts
export const colors = {
  accentYellow: "#ecad0a",
  bluePrimary: "#209dd7",
  purpleSecondary: "#753991",
  darkNavy: "#032147",
  grayText: "#888888",
};

// tailwind.config.ts
import type { Config } from "tailwindcss";
import { colors } from "./styles/colors";

const config: Config = {
  theme: {
    extend: {
      colors: {
        "accent-yellow": colors.accentYellow,
        "blue-primary": colors.bluePrimary,
        "purple-secondary": colors.purpleSecondary,
        "dark-navy": colors.darkNavy,
        "gray-text": colors.grayText,
      },
    },
  },
};
```

## Authentication Flow

1. **Login Page**: Users enter hardcoded credentials ("user"/"password")
2. **JWT Token**: Backend returns JWT token on successful login
3. **Token Storage**: Token stored in secure HTTP-only cookie
4. **Protected Routes**: All dashboard routes require valid JWT
5. **Auto-logout**: Token expiration handled gracefully
6. **Logout**: Clear token and redirect to login

## Kanban Board Architecture

### Data Flow

1. **Initial Load**: Fetch board data from `/api/boards`
2. **Real-time Updates**: WebSocket connection for live updates
3. **Optimistic Updates**: UI updates immediately, syncs with backend
4. **Error Handling**: Rollback on sync failure with user notification

### Drag & Drop Implementation

- **@dnd-kit/core**: Core DnD functionality
- **@dnd-kit/sortable**: Sortable lists for columns
- **@dnd-kit/utilities**: Utility functions
- Custom sensors for touch/mouse support

### Card Operations

- **Create**: Click "Add Card" button in column
- **Edit**: Double-click card or use context menu
- **Move**: Drag between columns or use move dialog
- **Delete**: Context menu or card options

## AI Chat Integration

### Chat Interface

- **Sidebar Toggle**: Button in header to open/close chat
- **Message Thread**: Chronological display of conversation
- **Input Area**: Text input with send button
- **Typing Indicator**: Shows when AI is processing
- **Markdown Support**: AI responses rendered as markdown

### AI Communication

1. **User Message**: Sent to `/api/ai/chat` with conversation history
2. **AI Processing**: Backend calls OpenRouter with structured prompt
3. **Structured Response**: AI returns Pydantic-model validated response
4. **UI Update**: Chat displays response, Kanban updates if needed
5. **Real-time Sync**: WebSocket notifies frontend of board changes

### WebSocket Implementation

- **Connection**: Establish on login, close on logout
- **Reconnection**: Automatic reconnection with exponential backoff
- **Message Types**:
  - `board_update`: Kanban board changed
  - `ai_response`: New AI message
  - `user_typing`: Typing indicators
- **Error Handling**: Graceful degradation to polling if WS fails

## State Management Strategy

### Local State (useState)

- UI state (modals, forms, toggles)
- Component-specific state

### Context API

- **AuthContext**: Authentication state
- **ThemeContext**: UI theme preferences
- **WebSocketContext**: WebSocket connection state

### Server State (React Query)

- **Boards data**: Cached with automatic refetch
- **AI conversations**: Paginated with infinite scroll
- **User preferences**: Optimistic updates

### Global State (Zustand - if needed)

- **Complex UI state**: Multi-step workflows
- **Cross-component state**: Chat visibility, notifications

## Performance Optimizations

### Code Splitting

- Dynamic imports for heavy components
- Route-based code splitting
- Lazy loading for below-fold content

### Image Optimization

- NextJS Image component
- Responsive images with srcset
- Lazy loading for images

### Data Fetching

- React Query for caching and background updates
- Optimistic updates for better UX
- Request deduplication

### Bundle Optimization

- Tree shaking with ES modules
- Code splitting by route
- Minimal dependencies

## Testing Strategy

### Unit Tests (Jest)

- **Components**: Render and interaction tests
- **Hooks**: Custom hook behavior
- **Utils**: Utility function correctness

### Integration Tests (React Testing Library)

- **User Flows**: Login, card creation, drag & drop
- **API Integration**: Mock API responses
- **State Management**: Context and store interactions

### E2E Tests (Playwright)

- **Critical Paths**: Full user journeys
- **Cross-browser**: Chrome, Firefox, Safari
- **Performance**: Load times and responsiveness

### Visual Tests

- **Snapshot Testing**: UI consistency
- **Responsive Testing**: Different screen sizes
- **Accessibility**: WCAG compliance

## Accessibility Requirements

### ARIA Labels

- Proper labels for all interactive elements
- Screen reader support for drag & drop
- Keyboard navigation for all features

### Keyboard Support

- Tab navigation through all elements
- Keyboard shortcuts for common actions
- Escape key to close modals

### Color Contrast

- Meet WCAG AA standards (4.5:1 ratio)
- Color-blind friendly palette
- High contrast mode support

## Responsive Design

### Breakpoints

- **Mobile**: < 640px
- **Tablet**: 640px - 1024px
- **Desktop**: > 1024px

### Mobile Considerations

- Touch-friendly drag handles
- Simplified card editing
- Collapsible sidebar on small screens

### Tablet Considerations

- Split view for chat and board
- Adjustable column widths
- Gesture support for navigation

## Error Handling

### User-facing Errors

- **Network Errors**: Retry with exponential backoff
- **Validation Errors**: Clear inline feedback
- **Permission Errors**: Redirect to login

### Developer-facing Errors

- **Error Boundaries**: Catch React errors
- **Error Logging**: Sentry or similar service
- **Error Reporting**: User feedback mechanism

### Graceful Degradation

- **Offline Mode**: Local storage for changes
- **API Failure**: Fallback to cached data
- **WebSocket Failure**: Polling fallback

## Security Considerations

### Client-side Security

- **XSS Prevention**: Sanitize user input
- **CSRF Protection**: SameSite cookies
- **JWT Security**: HTTP-only cookies

### Data Protection

- **Sensitive Data**: Never store in localStorage
- **API Keys**: Environment variables only
- **User Data**: Encrypted in transit (HTTPS)

### Privacy

- **GDPR Compliance**: Cookie consent
- **Data Minimization**: Only collect necessary data
- **User Control**: Clear data deletion options

## Development Workflow

### Local Development

```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Run tests
npm test
npm run test:e2e

# Build for production
npm run build
```

### Code Quality

- **ESLint**: Code style enforcement
- **Prettier**: Code formatting
- **TypeScript**: Strict type checking
- **Husky**: Pre-commit hooks

### Deployment

- **Docker**: Containerized deployment
- **CI/CD**: Automated testing and deployment
- **Monitoring**: Performance and error tracking

## Future Enhancements

### Phase 2

- Multiple boards per user
- Team collaboration features
- Advanced card templates

### Phase 3

- File attachments on cards
- Calendar view integration
- Advanced AI features (summaries, suggestions)

### Phase 4

- Mobile app (React Native)
- Desktop app (Electron)
- Browser extensions
