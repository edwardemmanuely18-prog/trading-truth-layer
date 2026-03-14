type Props = {
  title: string;
  value: string;
  subtitle?: string;
};

export default function EvidenceCard({ title, value, subtitle }: Props) {
  return (
    <section className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
      <div className="flex items-start justify-between gap-3">
        <div>
          <h3 className="text-lg font-semibold text-slate-900">{title}</h3>
          {subtitle ? <p className="mt-1 text-sm text-slate-500">{subtitle}</p> : null}
        </div>
      </div>

      <pre className="mt-4 overflow-x-auto whitespace-pre-wrap break-words rounded-xl bg-slate-50 p-4 text-sm text-slate-700">
        {value}
      </pre>
    </section>
  );
}
