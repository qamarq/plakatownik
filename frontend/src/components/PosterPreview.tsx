import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from './ui/button';

interface Props {
  resultUrl: string;
}

export function PosterPreview({ resultUrl }: Props) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Plakat</CardTitle>
      </CardHeader>
      <CardContent className="flex flex-col items-center gap-4">
        <img src={resultUrl} alt="Wygenerowany plakat" className="max-h-[70vh] rounded-md border" />
        <Button asChild>
          <a href={resultUrl} download className="text-sm font-medium text-primary">
            Pobierz plakat
          </a>
        </Button>
      </CardContent>
    </Card>
  );
}
