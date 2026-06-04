Purpose

Define the authentication flow for the AI vulnerability scanning platform.

Authentication Method
JWT Authentication
Bearer Token
Password Hashing with bcrypt
Stateless authentication
Authentication Flow

Client Login
→ Backend validates credentials
→ JWT token generated
→ Token returned to frontend
→ Frontend stores token
→ Token attached to API requests

Roles
Role	Description
guest	Unauthenticated visitor
user	Registered authenticated user
admin	Full system administrator
Guest Access

Allowed:

Scan source code
Upload source file
View demo dashboard

Restricted:

History
Export report
Admin APIs
User Access

Allowed:

Personal scan history
Export reports
AI findings
Pattern explainability

Restricted:

System configuration
User management
Global analytics
Admin Access

Allowed:

Full system control
User management
Model management
Analytics dashboard
API monitoring