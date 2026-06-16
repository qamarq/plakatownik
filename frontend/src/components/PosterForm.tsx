import { Controller, useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';

import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Field, FieldError, FieldGroup, FieldLabel } from '@/components/ui/field';
import { Input } from '@/components/ui/input';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import type { PosterRequest, ThemeSummary } from '@/lib/types';

const posterFormSchema = z.object({
  city: z.string().min(1, 'Podaj miasto'),
  country: z.string().min(1, 'Podaj kraj'),
  theme: z.string().min(1, 'Wybierz motyw'),
  distance: z.coerce.number().min(500, 'Min. 500 m').max(20000, 'Maks. 20000 m'),
  width: z.coerce.number().min(1).max(20, 'Maks. 20 in'),
  height: z.coerce.number().min(1).max(20, 'Maks. 20 in'),
  format: z.enum(['png', 'svg', 'pdf']),
  display_city: z.string().optional(),
  display_country: z.string().optional(),
  font_family: z.string().optional(),
});

type PosterFormValues = z.infer<typeof posterFormSchema>;

interface Props {
  themes: ThemeSummary[];
  busy: boolean;
  onSubmit: (request: PosterRequest) => void;
}

const FORMATS = ['png', 'svg', 'pdf'] as const;

export function PosterForm({ themes, busy, onSubmit }: Props) {
  const form = useForm<PosterFormValues>({
    resolver: zodResolver(posterFormSchema),
    defaultValues: {
      city: 'Wrocław',
      country: 'Polska',
      theme: 'terracotta',
      distance: 4000,
      width: 12,
      height: 16,
      format: 'png',
      display_city: '',
      display_country: '',
      font_family: '',
    },
  });

  function handleValid(values: PosterFormValues) {
    onSubmit({
      ...values,
      display_city: values.display_city || undefined,
      display_country: values.display_country || undefined,
      font_family: values.font_family || undefined,
    });
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Nowy plakat</CardTitle>
      </CardHeader>
      <CardContent>
        <form onSubmit={form.handleSubmit(handleValid)}>
          <FieldGroup>
            <div className="grid grid-cols-2 gap-4">
              <Field data-invalid={!!form.formState.errors.city}>
                <FieldLabel htmlFor="city">Miasto</FieldLabel>
                <Input id="city" {...form.register('city')} />
                <FieldError errors={[form.formState.errors.city]} />
              </Field>
              <Field data-invalid={!!form.formState.errors.country}>
                <FieldLabel htmlFor="country">Kraj</FieldLabel>
                <Input id="country" {...form.register('country')} />
                <FieldError errors={[form.formState.errors.country]} />
              </Field>
            </div>

            <Controller
              name="theme"
              control={form.control}
              render={({ field, fieldState }) => (
                <Field data-invalid={fieldState.invalid}>
                  <FieldLabel>Motyw</FieldLabel>
                  <Select value={field.value} onValueChange={field.onChange}>
                    <SelectTrigger className="w-full">
                      <SelectValue placeholder="Wybierz motyw" />
                    </SelectTrigger>
                    <SelectContent>
                      {themes.map((t) => (
                        <SelectItem key={t.id} value={t.id}>
                          <span className="flex items-center gap-2">
                            <span
                              className="size-3 shrink-0 rounded-full border"
                              style={{
                                backgroundColor: t.road_primary,
                                borderColor: t.text,
                              }}
                            />
                            {t.name}
                          </span>
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                  <FieldError errors={[fieldState.error]} />
                </Field>
              )}
            />

            <div className="grid grid-cols-2 gap-4">
              <Field data-invalid={!!form.formState.errors.distance}>
                <FieldLabel htmlFor="distance">Promień (m, krótsza oś)</FieldLabel>
                <Input
                  id="distance"
                  type="number"
                  min={500}
                  max={20000}
                  step={500}
                  {...form.register('distance', { valueAsNumber: true })}
                />
                <FieldError errors={[form.formState.errors.distance]} />
              </Field>
            </div>

            <Controller
              name="format"
              control={form.control}
              render={({ field, fieldState }) => (
                <Field data-invalid={fieldState.invalid}>
                  <FieldLabel>Format</FieldLabel>
                  <Select value={field.value} onValueChange={field.onChange}>
                    <SelectTrigger className="w-full">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      {FORMATS.map((f) => (
                        <SelectItem key={f} value={f}>
                          {f.toUpperCase()}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                  <FieldError errors={[fieldState.error]} />
                </Field>
              )}
            />

            <details className="rounded-md border border-input p-3">
              <summary className="cursor-pointer text-sm font-medium">Opcje dodatkowe</summary>
              <FieldGroup className="mt-3">
                <Field>
                  <FieldLabel htmlFor="displayCity">Wyświetlana nazwa miasta</FieldLabel>
                  <Input
                    id="displayCity"
                    placeholder="domyślnie: nazwa miasta"
                    {...form.register('display_city')}
                  />
                </Field>
                <Field>
                  <FieldLabel htmlFor="displayCountry">Wyświetlana nazwa kraju</FieldLabel>
                  <Input
                    id="displayCountry"
                    placeholder="domyślnie: nazwa kraju"
                    {...form.register('display_country')}
                  />
                </Field>
                <Field>
                  <FieldLabel htmlFor="fontFamily">Czcionka z Google Fonts</FieldLabel>
                  <Input
                    id="fontFamily"
                    placeholder="np. Noto Sans JP (domyślnie: Roboto)"
                    {...form.register('font_family')}
                  />
                </Field>
              </FieldGroup>
            </details>

            <Button type="submit" disabled={busy} className="w-full">
              {busy ? 'Generowanie...' : 'Generuj plakat'}
            </Button>
          </FieldGroup>
        </form>
      </CardContent>
    </Card>
  );
}
