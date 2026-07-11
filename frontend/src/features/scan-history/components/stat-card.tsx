interface StatCardProps {
  title: string;
  value: string | number;
  description?: string;
}

export function StatCard({ title, value, description }: StatCardProps): JSX.Element {
  return (
    <article className="rounded-lg border border-border bg-surface-panel p-4 shadow-sm">
      <span className="text-[10px] font-semibold text-text-muted uppercase tracking-wider block">
        {title}
      </span>
      <p className="mt-2 font-mono text-3xl font-bold tracking-tight text-text-primary">
        {value}
      </p>
      {description ? (
        <p className="mt-1.5 text-xs text-text-muted leading-relaxed">
          {description}
        </p>
      ) : null}
    </article>
  );
}
