# Engineering Architecture Rules: Multi-Modal Emotion AI

You must strictly adhere to these architectural standards, patterns, and boundaries when generating or modifying code for this project.

---

## 1. Stack Boundaries & State
*   **Database Stack:** PostgreSQL ONLY (utilizing `postgres:alpine` images via Docker).
*   **Banned Technologies:** Supabase is completely deprecated. Do NOT inject Supabase clients, credentials (`SUPABASE_URL`, `SUPABASE_KEY`), or client-side real-time libraries anywhere in the codebase.
*   **Database I/O:** All database operations must be non-blocking and asynchronous. Use an async driver (e.g., `asyncpg`) along with an async SQLAlchemy/SQLModel or Tortoise ORM engine setup.

---

## 2. Strict Separation of Concerns (SoC)
Code must be isolated into distinct functional tiers. Never mix infrastructure, transport, and domain logic.

```text
[ Client/UI ] ──> [ Router/Endpoint ] ──> [ Service Layer ] ──> [ Database/Model Engine ]
                      (HTTP/Schemas)          (Business Logic)         (SQLAlchemy / Safetensors)
s