import { useEffect, useRef, useState } from 'react';
import { ImageIcon, MapPinned } from 'lucide-react';

import { ModeToggle } from '@/components/mode-toggle';
import { PosterForm } from '@/components/PosterForm';
import { PosterPreview } from '@/components/PosterPreview';
import { ProgressLog } from '@/components/ProgressLog';
import { ThemeProvider } from '@/components/theme-provider';
import { Card, CardContent } from '@/components/ui/card';
import { connectPosterSocket, fetchThemes, startPoster } from '@/lib/api';
import {
  isCompleteMessage,
  type JobState,
  type PosterRequest,
  type ProgressEvent,
  type ThemeSummary,
} from '@/lib/types';

function PosterownikApp() {
  const [themes, setThemes] = useState<ThemeSummary[]>([]);
  const [events, setEvents] = useState<ProgressEvent[]>([]);
  const [jobState, setJobState] = useState<JobState | null>(null);
  const [resultUrl, setResultUrl] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const socketRef = useRef<WebSocket | null>(null);

  useEffect(() => {
    fetchThemes()
      .then(setThemes)
      .catch((e) => setError(e.message));
    return () => socketRef.current?.close();
  }, []);

  async function handleSubmit(request: PosterRequest) {
    setError(null);
    setResultUrl(null);
    setEvents([]);
    socketRef.current?.close();

    try {
      const job = await startPoster(request);
      setJobState(job.status);

      const socket = connectPosterSocket(job.id, (data) => {
        if (isCompleteMessage(data)) {
          socket.close();
          if (data.status === 'error') {
            setError(data.error ?? 'Generowanie nie powiodło się');
            setJobState('error');
            return;
          }
          setResultUrl(data.result_url ?? null);
          setJobState('done');
          return;
        }
        setEvents((prev) => [...prev, data]);
      });
      socketRef.current = socket;
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Nie udało się uruchomić generowania');
    }
  }

  const busy = jobState === 'queued' || jobState === 'running';

  return (
    <div className="min-h-screen bg-gradient-to-b from-background via-background to-muted/30">
      <header className="sticky top-0 z-10 border-b bg-background/80 backdrop-blur-sm">
        <div className="mx-auto flex w-full max-w-6xl items-center justify-between px-6 py-4">
          <div className="flex items-center gap-2.5">
            <div className="flex size-9 items-center justify-center rounded-lg bg-primary text-primary-foreground">
              <MapPinned className="size-5" />
            </div>
            <div>
              <h1 className="text-lg font-semibold leading-none">Posterownik</h1>
              <p className="text-xs text-muted-foreground">Plakaty map z danych OpenStreetMap</p>
            </div>
          </div>
          <ModeToggle />
        </div>
      </header>

      <main className="mx-auto w-full max-w-6xl px-6 py-10">
        <div className="grid gap-6 lg:grid-cols-[minmax(0,1fr)_minmax(0,1fr)] lg:items-start">
          <div className="space-y-6">
            <PosterForm themes={themes} busy={busy} onSubmit={handleSubmit} />
            {jobState && <ProgressLog events={events} error={error} />}
          </div>

          <div className="lg:sticky lg:top-24">
            {resultUrl ? (
              <PosterPreview resultUrl={resultUrl} />
            ) : (
              <Card className="border-dashed">
                <CardContent className="flex min-h-80 flex-col items-center justify-center gap-3 text-center text-muted-foreground">
                  <div className="flex size-12 items-center justify-center rounded-full bg-muted">
                    <ImageIcon className="size-6" />
                  </div>
                  <div>
                    <p className="font-medium text-foreground">Tu pojawi się Twój plakat</p>
                    <p className="text-sm">Wypełnij formularz i kliknij „Generuj plakat”.</p>
                  </div>
                  {error && !jobState && <p className="text-sm text-destructive">{error}</p>}
                </CardContent>
              </Card>
            )}
          </div>
        </div>
      </main>

      <footer className="mx-auto w-full max-w-6xl px-6 py-8 text-center text-xs text-muted-foreground">
        Dane mapowe © OpenStreetMap contributors (ODbL)
      </footer>
    </div>
  );
}

export default function App() {
  return (
    <ThemeProvider defaultTheme="system" storageKey="posterownik-theme">
      <PosterownikApp />
    </ThemeProvider>
  );
}
