import { Suspense } from "react";
import ClaimsPageClient from "./ClaimsPageClient";

export default function PublicClaimsPage() {
  return (
    <Suspense
      fallback={
        <div className="min-h-screen bg-slate-50 text-slate-900">
          <div className="mx-auto max-w-[1400px] px-6 py-10">
            <section className="rounded-[32px] border border-slate-200 bg-white p-8 shadow-sm">
              <div className="text-xl text-slate-500">Loading public claims…</div>
            </section>
          </div>
        </div>
      }
    >
      <ClaimsPageClient />
    </Suspense>
  );
}