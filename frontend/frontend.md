# SYSTEM DIRECTIVE: AI Operations Hub - Phase 5 Frontend

## 🎯 Role & Objective
You are an Expert Frontend Architect and UI/UX Designer. Your task is to build the "Phase 5 Frontend Dashboard" for the AI Operations Hub. 

**CRITICAL CONSTRAINTS:**
1. **DO NOT modify any backend files.** The backend (FastAPI, LangGraph, n8n) is 100% complete and functional. You are restricted to the `frontend/` directory.
2. The backend runs in a Conda environment named `LearnAgents` on `http://127.0.0.1:8000`. You must ensure all frontend API calls point to this URL.
3. The frontend is a Next.js (App Router) + Tailwind CSS application.

---

## 🎨 Aesthetic & Design System (STRICT GUIDELINES)
Read these instructions carefully. You must avoid generic "AI slop" aesthetics (no purple gradients on white backgrounds, no default Inter/Roboto fonts, no cookie-cutter layouts). 

We are executing a **"Refined Utilitarian / High-End SaaS"** aesthetic. It must look like a premium, expensive internal tool used by a Fortune 500 operations team.

*   **Typography:** Pair a distinctive display font for headings (e.g., *Cabinet Grotesk*, *Clash Display*, or *Syne*) with a highly legible, technical font for data and body (e.g., *JetBrains Mono* or *General Sans*). DO NOT use Arial, Inter, or Roboto.
*   **Color Palette:** Use a high-contrast dark mode OR a stark, architectural light mode. 
    *   *Backgrounds:* Deep charcoal/off-black (`#0f1115`) or stark paper-white.
    *   *Accents:* Use ONE bold, sharp accent color (e.g., Electric Indigo, Acid Green, or Safety Orange) for primary actions and AI badges.
*   **Composition:** Use asymmetrical "Bento-box" grid layouts for the dashboard. Use generous negative space. Add subtle CSS noise textures or geometric grid-line backgrounds to create depth.
*   **Motion:** Implement staggered reveals on page load using CSS `animation-delay`. Add crisp, snappy hover states. Avoid slow, floaty animations.
*   **UI Details:** Use sharp corners (or very slight rounding like `rounded-sm`), thin borders (`border-gray-800`), and monospaced badges for metadata (e.g., `[ROUTE: SALES]`).

---

## 🔌 Backend API Integration Guide
The frontend must communicate with the existing FastAPI backend.

1. **Chat Endpoint:** `POST http://127.0.0.1:8000/api/v1/query`
   *   *Payload:* `{ "query": "string", "session_id": "string" }`
   *   *Response:* `{ "answer": "string", "sources": ["string"], "route_taken": "string", "requires_approval": boolean, "extracted_data": {} }`
2. **Upload Endpoint:** `POST http://127.0.0.1:8000/api/v1/upload`
   *   *Payload:* `multipart/form-data` (key: `file`, accepts `.pdf` or `.txt`)
3. **Health Endpoint:** `GET http://127.0.0.1:8000/api/v1/health`

---

## 🏗️ Feature Requirements

Build a multi-page Next.js application with a persistent sidebar navigation.

### 1. The Chat Interface (`/chat`)
This is the core interaction screen.
*   **Message Bubbles:** Differentiate User and AI visually. 
*   **Metadata Badges:** If the AI response includes `route_taken` or `requires_approval: true`, display these as highly visible, technical-looking tags above the AI's message.
*   **Sources Panel:** If `sources` are returned, display them in a sleek, collapsible accordion or a monospaced footer below the message.
*   **Input Area:** A clean, sticky bottom input bar. Disable the input and show a sleek "Processing..." animation while waiting for the backend.

### 2. The Dashboard (`/dashboard`)
A high-level overview of the system.
*   **Bento-Box Layout:** Create a grid showing mock statistics (e.g., "Total Queries: 1,204", "Active Agents: 4", "Escalations Pending: 2").
*   **Approval Queue:** A dedicated card showing a list of queries that were flagged with `requires_approval: true`. (You can mock this list for the UI, but style it to look like an actionable inbox).
*   **Logs/Traces:** A terminal-like window displaying mock system logs (e.g., `[ROUTER] Query routed to SALES`). Use a monospace font here.

### 3. Document Management (`/knowledge`)
The interface for the RAG ingestion pipeline.
*   **Upload Zone:** A large, beautifully designed drag-and-drop zone.
*   **Upload Logic:** Wire this up to the `POST /api/v1/upload` endpoint. Show a progress state and a success toast notification when the backend returns a 200 OK.
*   **Document List:** A table or grid displaying uploaded documents (you can mock the list of existing documents, but the upload action must be real).

### 4. Admin & Agent Monitoring (`/admin`)
*   **Agent Status:** Visual cards representing the Router, Support, Sales, and Escalation agents. Show them as "Online" with glowing status indicators.
*   **Workflow Toggles:** Beautifully styled toggle switches to enable/disable specific n8n workflows (UI only for now).

---

## 🚀 Execution Steps for the Agent
1. Initialize the required fonts (via `next/font/google` or external imports).
2. Set up the global CSS with the chosen aesthetic (variables, noise textures, etc.).
3. Create the layout wrapper with the sidebar navigation.
4. Build the Chat interface and wire it to the `/query` endpoint.
5. Build the Knowledge interface and wire it to the `/upload` endpoint.
6. Build the Dashboard and Admin pages with high-fidelity mock data.
7. Ensure all components are responsive and visually striking.

**DO NOT output generic Tailwind templates. Be creative, be bold, and make this look like a flagship portfolio piece.**