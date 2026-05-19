---
name: monaco-editor
description: Monaco Editor integration skill cho AI vulnerability analysis platform.
license: MIT
---

# Monaco Editor Skill
## Mission
Biến Monaco Editor thành code analysis interface chuyên nghiệp.
## Core Rules
- Monaco phải là trung tâm analysis UI
- Readonly khi hiển thị kết quả scan
- Editable khi nhập source code
## Required Features
- Syntax highlighting
- Line numbers
- Vulnerable line decorations
- Severity markers
- Minimap optional
## Decorations
- LOW → green gutter
- MEDIUM → yellow gutter
- HIGH → orange gutter
- CRITICAL → red gutter
## Interaction
- Click finding → jump line
- Hover line → tooltip issue
- Scroll sync findings/editor
## Performance
- Dynamic import Monaco
- Debounce editor updates
- Không rerender toàn editor
## Theme
- Dark mode ưu tiên
- High contrast
## Responsive
- Full width mobile
- Min height 500px desktop
## Forbidden
- Không disable line numbers
- Không plain textarea
- Không rerender editor liên tục
## QA Checklist
- Highlight đúng line
- Scroll sync đúng
- Tooltip đúng
- Responsive đúng
- Performance ổn định