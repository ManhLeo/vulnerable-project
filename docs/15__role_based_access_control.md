RBAC Overview

The system uses Role-Based Access Control (RBAC).

Each authenticated user has exactly one role.

Role Hierarchy

guest
↓
user
↓
admin

Permission Matrix
Feature	Guest	User	Admin
Scan code	YES	YES	YES
Upload file	YES	YES	YES
View own history	NO	YES	YES
Export reports	NO	YES	YES
AI confidence	YES	YES	YES
Findings panel	YES	YES	YES
Delete scans	NO	NO	YES
View all scans	NO	NO	YES
Change model config	NO	NO	YES
Manage users	NO	NO	YES
Backend Enforcement

FastAPI dependencies are used to enforce authorization.

Example:

Depends(require_role(["admin"]))