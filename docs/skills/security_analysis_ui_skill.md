---
name: security-analysis-ui
description: UI/UX skill cho AI vulnerability detection platform với explainability visualization, Monaco integration và security-focused workflows.
license: MIT
---

# Security Analysis UI Skill
## Mission
Thiết kế frontend giống một security analysis platform thực tế thay vì dashboard thông thường.
## Design Intent
UI phải thể hiện:
- AI-powered analysis
- security severity
- explainability
- code inspection workflow
## Core UX Principles
- Code là trung tâm UI
- Findings phải dễ scan
- Severity phải nổi bật
- Risk phải hiểu ngay lập tức
- Loading phải tạo cảm giác AI đang phân tích
## Severity Rules
- LOW → green
- MEDIUM → yellow
- HIGH → orange
- CRITICAL → red
## Findings Rules
Mỗi finding phải có:
- pattern
- issue
- severity
- line number
- code snippet
## Findings UI
- Badge severity rõ ràng
- Click finding scroll tới line
- Hover line highlight finding
- Multiple findings support
## Monaco Integration
- Highlight vulnerable lines
- Gutter decorations
- Readonly result mode
- Syntax highlighting bắt buộc
- Scroll sync với findings list
## Scan Workflow
Upload/Paste Code
→ Loading
→ AI Analysis
→ Findings
→ History Persistence
## Result Page Rules
Bắt buộc hiển thị:
- Vulnerable status
- Confidence score
- Risk level
- Findings count
- Highlighted code
## Risk Visualization
- Risk badge lớn
- Confidence progress bar
- Severity counters
- Findings grouped by severity
## History Page Rules
Mỗi record hiển thị:
- filename
- language
- risk level
- vulnerable status
- created_at
## Empty States
- Không findings → "No vulnerabilities detected"
- Không history → empty illustration/message
## Loading States
- Scanning animation
- Skeleton UI
- Disable submit khi scanning
## Error States
- Upload failed
- API unavailable
- Model unavailable
- Invalid file
## Responsive Rules
- Monaco responsive height
- Findings stack trên mobile
- Tables scroll horizontal
## Interaction Rules
- Finding click → jump to line
- Hover line → show tooltip
- Copy code supported
## Forbidden
- Không generic dashboard UI
- Không plain tables không highlight
- Không severity text không màu
- Không overload chart vô nghĩa
## QA Checklist
- Line highlight đúng
- Severity colors đúng
- Findings sync đúng
- Monaco render đúng
- Responsive hoạt động
- Empty/loading/error state đầy đủ