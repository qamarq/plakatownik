import type { JobStatus, PosterRequest, PosterSocketMessage, ThemeSummary } from './types';

const API_BASE = '/api';

async function asJson<T>(res: Response): Promise<T> {
  if (!res.ok) {
    const detail = await res.json().catch(() => null);
    throw new Error(detail?.detail ?? `Request failed (${res.status})`);
  }
  return res.json();
}

export function fetchThemes(): Promise<ThemeSummary[]> {
  return fetch(`${API_BASE}/themes`).then((r) => asJson(r));
}

export function startPoster(req: PosterRequest): Promise<JobStatus> {
  return fetch(`${API_BASE}/posters`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(req),
  }).then((r) => asJson(r));
}

export function getPoster(jobId: string): Promise<JobStatus> {
  return fetch(`${API_BASE}/posters/${jobId}`).then((r) => asJson(r));
}

export function connectPosterSocket(
  jobId: string,
  onMessage: (data: PosterSocketMessage) => void,
): WebSocket {
  const protocol = window.location.protocol === 'https:' ? 'wss' : 'ws';
  const ws = new WebSocket(`${protocol}://${window.location.host}/ws/posters/${jobId}`);
  ws.onmessage = (msg) => onMessage(JSON.parse(msg.data));
  return ws;
}
