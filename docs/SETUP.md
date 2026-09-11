# Local setup

## 1. Start the Command Center backend

```bash
cd backend
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Backend health:

```text
http://localhost:8000/api/health
```

## 2. Start the redesigned frontend

```bash
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173`.

## 3. Prepare a Linux ATS host

Install and start OmniLab Android Test Station using the official Android Test Station tooling. ATS provides a REST API and an OpenAPI specification. The OpenAPI document is normally available at:

```text
http://<linux-host>:8000/_ah/api_docs/api.json
```

The actual port/base URL must match that host's ATS configuration.

## 4. Register the Linux host

From the Command Center dashboard, add the ATS base URL, then use **Check ATS & Discover API**.

The backend reads the real OpenAPI specification and exposes its operation IDs to the Command Center integration layer. This avoids embedding undocumented ATS paths in our code.

## 5. Map semantic operations

The server model supports mappings for:

- `list_devices`
- `create_run`
- `get_run`
- `cancel_run`

Use operation IDs returned by the actual ATS host. A later UI surface will make these mappings editable directly from Administration.

## Design constraint

The legacy custom Linux agent is not the primary execution path in this repository. ATS/Tradefed owns Linux-side execution; Command Center owns workflow and UX.
