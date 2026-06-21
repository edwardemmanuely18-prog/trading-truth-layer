import { ReactNode } from "react";
import { THEME } from "@/lib/institutionalTheme";

type Props = {
  title: string;
  children: ReactNode;
};

export default function AnalyticsCard({
  title,
  children,
}: Props) {
  return (
    <div className={`${THEME.card.analytics} p-6`}>
      <h3 className={THEME.section.title}>
        {title}
      </h3>

      <div className="mt-6">
        {children}
      </div>
    </div>
  );
}