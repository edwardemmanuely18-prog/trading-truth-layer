import { THEME } from "@/lib/institutionalTheme";

type Props = {
  title: string;
  value: string | number;
  subtitle?: string;
};

export default function MetricCard({
  title,
  value,
  subtitle,
}: Props) {
  return (
    <div className={`${THEME.card.executive} p-6`}>
      <div className={THEME.metric.label}>
        {title}
      </div>

      <div className={THEME.metric.value}>
        {value}
      </div>

      {subtitle && (
        <div className={THEME.metric.subtitle}>
          {subtitle}
        </div>
      )}
    </div>
  );
}