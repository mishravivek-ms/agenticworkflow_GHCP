# Planning: Basic Authentication Flow

This file is read by the GitHub Actions workflow to create agent issues.  
Full implementation details are in [`planned/plan.md`](planned/plan.md).

## Summary

Build a **FastAPI + FastUI** web application with a basic username/password authentication flow.

- **UI/UX**: A login page (username + password fields + submit button) built with FastUI Python components, plus a post-login dashboard page.
- **Backend**: A FastAPI REST endpoint (`POST /api/login`) that validates credentials against hardcoded values (`username` / `passcode`).
- **Testing**: pytest tests covering successful login, failed login, missing fields, and UI route smoke tests.

See [`planned/plan.md`](planned/plan.md) for the full implementation plan including all code, file structure, API spec, and task checklist.
