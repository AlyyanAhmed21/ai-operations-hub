# SYSTEM DIRECTIVE: AI Operations Hub - Full-Stack Data Integration

## 🎯 Role & Objective
You are an Expert Full-Stack Developer. The user has a beautiful, fully styled frontend (`index.html`) and a working FastAPI/LangGraph backend. 

Currently, the frontend contains hardcoded placeholder data. Your objective is to connect the frontend to the backend so it displays **real data**, specifically focusing on Connection Status, Document Management, and Agent Status.

**CRITICAL CONSTRAINTS:**
1. **PRESERVE THE DESIGN:** The CSS and HTML structure in `index.html` is perfect. When making lists dynamic (like the documents table or agent cards), you MUST reuse the exact same CSS classes and HTML structure. Do not alter the aesthetic.
2. **ENVIRONMENT:** The backend runs in a Conda environment named `LearnAgents`.
3. **BACKEND PATH:** The backend is located in the `backend/` directory. The frontend is served via `server.js`.

---

## 🛠️ Task 1: Real-Time Connection Status
Currently, the "System Online" (Sidebar) and "Connected" (Chat Header) badges are hardcoded.

**Backend Action:**
* Ensure `GET /api/v1/health` exists in `backend/api/routes.py` and returns `{"status": "healthy", "version": "1.0.0"}`.

**Frontend Action (`index.html`):**
* Write a JavaScript function that pings `http://127.0.0.1:8000/api/v1/health` every 10 seconds.
* If it returns 200 OK, keep the badges green/acid (`badge-acid`, `status-dot` pulsing).
* If it fails or catches an error, change the badges to red (`badge-danger`, text: "Disconnected", stop the pulse animation).

---

## 📁 Task 2: Real Document Management (The `docs/` folder)
Currently, the "Indexed Documents" table is hardcoded, and uploaded files are deleted after ingestion.

**Backend Action (`backend/api/routes.py` & `backend/rag/ingestion.py`):**
1. Update the `POST /api/v1/upload` endpoint. Instead of saving to a `temp/` folder and deleting it, save the uploaded files permanently into a `backend/docs/` directory.
2. Create a new endpoint: `GET /api/v1/documents`.
   * This endpoint should read the `backend/docs/` directory.
   * It must return a JSON list of files containing: `id` (generate a simple ID), `filename`, `type` (PDF/TXT), `size` (formatted in KB/MB), and `ingested_date` (file creation date).

**Frontend Action (`index.html`):**
* On page load, fetch `http://127.0.0.1:8000/api/v1/documents`.
* Clear the hardcoded `<tbody>` in the Knowledge Base table.
* Dynamically generate the `<tr>` rows using the exact same HTML structure, SVG icons, and CSS classes (`id-cell`, `file-cell`, `type-pill`, `muted-cell`, `action-btn`) as the original hardcoded rows.
* Update the `handleUpload` JS function to refresh this table automatically after a successful upload.

---

## 🤖 Task 3: Dynamic Agents & Dashboard Stats
Currently, the Dashboard hardcodes "4 Active Agents", and the Admin Panel hardcodes 4 agent cards. We recently added a 5th agent (General Agent).

**Backend Action (`backend/api/routes.py`):**
* Create a new endpoint: `GET /api/v1/system/status`.
* Return a JSON object containing:
  ```json
  {
    "active_agents_count": 5,
    "agents": [
      {"name": "Router Agent", "role": "Primary Traffic Controller", "status": "online", "latency": "12ms"},
      {"name": "Support Agent", "role": "Policy & Knowledge", "status": "online", "latency": "45ms"},
      {"name": "Sales Agent", "role": "Pricing & Enterprise", "status": "online", "latency": "38ms"},
      {"name": "Escalation Agent", "role": "Human Handoff", "status": "standby", "latency": "—"},
      {"name": "General Agent", "role": "Greetings & Navigation", "status": "online", "latency": "15ms"}
    ]
  }

  Frontend Action (index.html):
Fetch http://127.0.0.1:8000/api/v1/system/status on load.
Update the "Active Agents" number on the Dashboard view.
Clear the hardcoded .agents-grid in the Admin view.
Dynamically render the 5 agent cards based on the JSON response.
Crucial: Maintain the exact HTML structure of .agent-card. If status is "online", use the badge-acid pulsing dot. If "standby", use the badge-muted style.
🚀 Execution Rules for the AI Agent
Start by modifying the Python backend (routes.py and ingestion.py) to create the new endpoints and the docs/ folder logic.
Then, modify the <script> section of index.html to add the fetch calls and DOM manipulation.
DO NOT change the CSS <style> block.
DO NOT break the existing Chat/LangGraph functionality.
code
Code
***

### Why this prompt is bulletproof:
1. **It solves the `docs/` folder issue:** Instead of throwing away your PDFs, the backend will now save them to `backend/docs/`. The frontend will read that exact folder to build the table.
2. **It adds the 5th Agent:** By creating a `/system/status` endpoint, the UI will dynamically generate the cards. If you ever add a 6th agent in the future, it will automatically appear in the UI!
3. **It adds real Health Polling:** The UI will ping the server every 10 seconds. If you turn off your Python server, the UI will instantly turn red and say "Disconnected."