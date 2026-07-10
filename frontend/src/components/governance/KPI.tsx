type Props = {
  title: string;
  value: string | number;
  subtitle?: string;
};

export default function KPI({
  title,
  value,
  subtitle,
}: Props) {
  return (
    <div className="rounded-2xl border bg-slate-50 p-5">
      <div className="text-xs font-semibold uppercase tracking-wider text-slate-500">
        {title}
      </div>

      <div className="mt-3 text-3xl font-bold text-slate-900">
        {value}
      </div>

      {subtitle ? (
        <div className="mt-2 text-sm text-slate-500">
          {subtitle}
        </div>
      ) : null}
    </div>
  );
}