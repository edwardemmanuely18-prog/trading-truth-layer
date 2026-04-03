import Link from "next/link";

export default function VerifyNotFound() {
  return (
    <main className="min-h-screen bg-slate-50">
      <div className="mx-auto max-w-3xl px-6 py-20">
        <div className="rounded-2xl border border-slate-200 bg-white p-8 shadow-sm">
          <p className="text-sm font-medium text-slate-500">Trading Truth Layer</p>
          <h1 className="mt-3 text-3xl font-semibold text-slate-950">Claim not found</h1>
          <p className="mt-4 text-sm leading-6 text-slate-600">
            The verification hash did not match any currently resolvable claim record.
          </p>
          <Link
            href="/"
            className="mt-6 inline-flex rounded-full bg-slate-900 px-4 py-2 text-sm font-medium text-white hover:bg-slate-800"
          >
            Go home
          </Link>
        </div>
      </div>
    </main>
  );
}