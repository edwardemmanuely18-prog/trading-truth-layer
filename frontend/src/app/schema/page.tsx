import Navbar from "../../components/Navbar";
import ClaimSchemaForm from "../../components/ClaimSchemaForm";

export default function SchemaPage() {
  return (
    <div className="min-h-screen bg-slate-50 text-slate-900">
      <Navbar />

      <main className="mx-auto max-w-5xl px-6 py-10">
        <div className="mb-8">
          <h1 className="text-3xl font-bold">Claims Schema Builder</h1>
          <p className="mt-2 text-slate-600">
            Define the exact scope, trade universe, and methodology for a verified performance claim.
          </p>
        </div>

        <ClaimSchemaForm />
      </main>
    </div>
  );
}