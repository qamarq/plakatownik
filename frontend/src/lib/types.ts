export interface ThemeSummary {
  id: string;
  name: string;
  description: string;
  bg: string;
  text: string;
  road_primary: string;
  water: string;
}

export interface PosterRequest {
  city: string;
  country: string;
  theme: string;
  distance: number;
  width: number;
  height: number;
  format: 'png' | 'svg' | 'pdf';
  latitude?: number;
  longitude?: number;
  country_label?: string;
  display_city?: string;
  display_country?: string;
  font_family?: string;
}

export type StepStatus = 'started' | 'done' | 'error';

export interface ProgressEvent {
  step: string;
  status: StepStatus;
  message: string;
  elapsed?: number | null;
}

export type JobState = 'queued' | 'running' | 'done' | 'error';

export interface CompleteMessage {
  step: 'complete';
  status: JobState;
  error?: string | null;
}

export type PosterSocketMessage = ProgressEvent | CompleteMessage;

export function isCompleteMessage(message: PosterSocketMessage): message is CompleteMessage {
  return message.step === 'complete';
}

export interface JobStatus {
  id: string;
  status: JobState;
  request: PosterRequest;
  events: ProgressEvent[];
  error?: string | null;
  result_url?: string | null;
}

export const STEP_ORDER = [
  'geocode',
  'fetch_graph',
  'fetch_water',
  'fetch_parks',
  'render',
  'save',
] as const;

export const STEP_LABELS: Record<string, string> = {
  geocode: 'Geokodowanie miasta',
  fetch_graph: 'Pobieranie sieci dróg',
  fetch_water: 'Pobieranie wody',
  fetch_parks: 'Pobieranie parków',
  render: 'Renderowanie plakatu',
  save: 'Zapisywanie pliku',
};
