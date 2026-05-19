# Frontend Rules
## Mission
Xây dựng frontend cho AI Vulnerability Detection Platform bằng Next.js + TypeScript với kiến trúc rõ ràng, tái sử dụng cao, responsive và dễ maintain.
## Core Stack
- Next.js App Router
- TypeScript strict mode
- TailwindCSS
- shadcn/ui
- Axios
- Monaco Editor
- React Query hoặc SWR
## Architecture Rules
- Không gọi API trực tiếp trong component UI
- Tách api client riêng trong lib/api
- Không viết business logic trong page
- Component phải reusable
- Tách presentation và logic
- Không hardcode endpoint
- Không hardcode màu severity
## Required Structure
src/
app/
components/
features/
lib/
services/
types/
hooks/
styles/
## Folder Rules
- app/: routing
- components/: reusable UI
- features/: business UI modules
- services/: API calls
- lib/: utility/helper/config
- hooks/: custom hooks
- types/: global types
## API Rules
- Tất cả API dùng axios instance chung
- Handle loading/error globally
- Typed response bắt buộc
- Không any
## State Rules
- Local state ưu tiên useState
- Server state dùng React Query/SWR
- Không prop drilling sâu
## Component Rules
- Một component chỉ một responsibility
- Component > 300 dòng phải split
- Không inline styles
- Tailwind utility-first
## UI Rules
- Responsive mobile-first
- Loading state bắt buộc
- Error state bắt buộc
- Empty state bắt buộc
- Skeleton loading ưu tiên hơn spinner
## Accessibility
- Keyboard navigation bắt buộc
- Focus visible bắt buộc
- Contrast đạt WCAG AA
- Button phải có aria-label nếu icon-only
## Monaco Rules
- Readonly result mode
- Highlight vulnerable lines
- Severity decorations
- Line numbers luôn visible
## Security Rules
- Không render raw HTML
- Validate upload client-side
- Không expose internal errors
## Performance Rules
- Dynamic import cho Monaco
- Lazy load charts
- Memoize heavy components
## Error Handling
- Toast cho API errors
- Retry cho network errors
- Graceful fallback UI
## Naming Rules
- PascalCase cho components
- camelCase cho variables
- kebab-case cho folders
## Forbidden
- Không dùng Redux
- Không dùng inline fetch trong component
- Không dùng giant components
- Không duplicated UI logic
## Required Pages
- Home
- Scan Result
- Scan History
- Optional Dashboard
## QA Checklist
- Responsive đúng
- Không console error
- Không TypeScript error
- API typed đầy đủ
- Loading/error state hoạt động
- Monaco highlight đúng
- Severity colors đúng