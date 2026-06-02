const styles: Record<string, string> = {
  Critical: "bg-rose-100 text-rose-800 border-rose-200",
  High: "bg-rose-100 text-rose-800 border-rose-200",
  Medium: "bg-amber-100 text-amber-800 border-amber-200",
  Low: "bg-emerald-100 text-emerald-800 border-emerald-200",
};

export function SeverityBadge({ value }: { value: string }) {
  return (
    <span className={`inline-flex items-center rounded border px-2 py-1 text-xs font-semibold ${styles[value] || styles.Low}`}>
      {value}
    </span>
  );
}
