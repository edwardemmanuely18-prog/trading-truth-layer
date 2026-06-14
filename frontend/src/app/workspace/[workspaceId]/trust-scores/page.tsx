import Navbar from "../../../../components/Navbar";

export default function Page() {
  return (
    <div className="min-h-screen bg-slate-50">
      <Navbar />

      <div className="mx-auto max-w-7xl px-6 py-10">
        <div className="rounded-2xl border bg-white p-8 shadow-sm">
          <h1 className="text-3xl font-bold">
            Institutional Module
          </h1>

          <p className="mt-4 text-slate-600">
            Reserved for future implementation.
          </p>
        </div>
      </div>
    </div>
  );
}