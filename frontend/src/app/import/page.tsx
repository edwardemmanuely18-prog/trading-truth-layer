import Navbar from "../../components/Navbar";
import ImportForm from "../../components/ImportForm";

export default function ImportPage() {
  return (
    <div className="min-h-screen bg-slate-50 text-slate-900">
      <Navbar />

      <main className="mx-auto max-w-4xl px-6 py-10">
        <div className="mb-8">
          <h1 className="text-3xl font-bold">Trade Import</h1>
          <p className="mt-2 text-slate-600">
            Add manual trades now. CSV ingestion will plug into this workflow next.
          </p>
        </div>

        <ImportForm />
      </main>
    </div>
  );
}