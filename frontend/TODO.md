# Phase 1 — App Shell + Global Design System

- [x] 1) Centralize light-first design tokens in `src/styles/globals.css`
- [x] 2) Extend token mappings in `tailwind.config.ts`
- [x] 3) Create reusable UI primitives
  - [x] `src/components/ui/button.tsx`
  - [x] `src/components/ui/card.tsx`
  - [x] `src/components/ui/badge.tsx`
  - [x] `src/components/ui/input.tsx`
  - [x] `src/components/ui/skeleton.tsx`
- [x] 4) Create layout building blocks
  - [x] `src/components/layout/sidebar-nav.tsx`
  - [x] `src/components/layout/topbar-status.tsx`
- [x] 5) Redesign `src/components/layout/app-shell.tsx`
  - [x] Desktop sidebar width 240px
  - [x] Topbar/status bar
  - [x] Responsive mobile collapse
  - [x] Active route visible
- [x] 6) Update `src/app/layout.tsx` wrappers/classes if needed
- [x] 7) Migrate loading foundation to new skeleton primitive
  - [x] `src/components/common/loading-state.tsx`
- [x] 8) Validation
  - [x] `npm run lint`
  - [x] `npm run build`
  - [ ] Runtime check (shell responsiveness and active route)

# Phase 2 — Integration & Quality

- [ ] 9) Integrate API with Backend endpoints
- [ ] 10) Setup State Management (Zustand)
- [ ] 11) Add Error Boundaries for network failures
