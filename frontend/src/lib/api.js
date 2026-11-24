/**
 * Thin wrapper around fetch for the ResumeIQ backend.
 * In development VITE_API_URL is empty and Vite proxies /api to the FastAPI server.
 */
export const API_BASE = (import.meta.env.VITE_API_URL || "").replace(/\/$/, "");

// Shown when the backend can't be reached. A free hosted backend sleeps when idle and
// takes up to a minute to wake, so the hosted build suggests waiting and retrying.
const UNREACHABLE = API_BASE || import.meta.env.PROD
  ? "The ResumeIQ server is waking up or unavailable. Please wait 30–60 seconds and try again."
  : "Cannot reach the ResumeIQ server. Is the backend running on port 8000?";

async function request(path, options = {}) {
  let res;
  try {
    res = await fetch(`${API_BASE}${path}`, options);
  } catch {
    throw new Error(UNREACHABLE);
  }
  if (!res.ok) {
    let message = `Request failed (${res.status})`;
    try {
      const body = await res.json();
      // FastAPI returns { detail: "..." } or { detail: [{ msg }] } for validation errors
      if (typeof body.detail === "string") message = body.detail;
      else if (Array.isArray(body.detail)) message = body.detail.map((d) => d.msg).join(", ");
    } catch {
      /* non-JSON error body */
    }
    if (res.status >= 502 && res.status <= 504) message = UNREACHABLE;
    throw new Error(message);
  }
  return res.json();
}

export const api = {
  health: () => request("/api/health"),
  roles: () => request("/api/roles"),
  analyze: ({ file, jobDescription, jobRole }) => {
    const form = new FormData();
    form.append("file", file);
    form.append("job_description", jobDescription);
    form.append("job_role", jobRole || "");
    return request("/api/analyze", { method: "POST", body: form });
  },
  history: () => request("/api/history"),
  getAnalysis: (id) => request(`/api/history/${id}`),
  deleteAnalysis: (id) => request(`/api/history/${id}`, { method: "DELETE" }),
  reportUrl: (id) => `${API_BASE}/api/history/${id}/report`,
};
