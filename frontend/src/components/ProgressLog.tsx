import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Progress } from '@/components/ui/progress';
import { cn } from '@/lib/utils';
import { STEP_LABELS, STEP_ORDER, type ProgressEvent } from '@/lib/types';

interface Props {
  events: ProgressEvent[];
  error?: string | null;
}

function latestByStep(events: ProgressEvent[]) {
  const latest = new Map<string, ProgressEvent>();
  for (const event of events) latest.set(event.step, event);
  return latest;
}

export function ProgressLog({ events, error }: Props) {
  const latest = latestByStep(events);
  const doneCount = STEP_ORDER.filter((step) => latest.get(step)?.status === 'done').length;
  const percent = (doneCount / STEP_ORDER.length) * 100;

  return (
    <Card>
      <CardHeader>
        <CardTitle>Postęp</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <Progress value={percent} />
        <ul className="space-y-2 text-sm">
          {STEP_ORDER.map((step) => {
            const event = latest.get(step);
            const status = event?.status ?? 'pending';
            return (
              <li key={step} className="flex items-center justify-between">
                <span
                  className={cn(
                    'flex items-center gap-2',
                    status === 'done' && 'text-foreground',
                    status === 'started' && 'text-primary',
                    status === 'pending' && 'text-muted-foreground',
                    status === 'error' && 'text-destructive',
                  )}
                >
                  <StatusDot status={status} />
                  {STEP_LABELS[step]}
                </span>
                <span className="text-xs text-muted-foreground">
                  {event?.message}
                  {event?.elapsed != null ? ` · ${event.elapsed.toFixed(1)}s` : ''}
                </span>
              </li>
            );
          })}
        </ul>
        {error && <p className="text-sm text-destructive">Błąd: {error}</p>}
      </CardContent>
    </Card>
  );
}

function StatusDot({ status }: { status: string }) {
  return (
    <span
      className={cn(
        'h-2 w-2 rounded-full',
        status === 'done' && 'bg-green-500',
        status === 'started' && 'animate-pulse bg-primary',
        status === 'pending' && 'bg-muted-foreground/30',
        status === 'error' && 'bg-destructive',
      )}
    />
  );
}
