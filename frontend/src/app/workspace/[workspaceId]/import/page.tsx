import Navbar from "../../../../components/Navbar";
import ImportForm from "../../../../components/ImportForm";

type PageProps = {
  params: Promise<{
    workspaceId: string;
  }>;
};

export default async function WorkspaceImportPage({ params }: PageProps) {
  const resolved = await params;
  const workspaceId = Number(resolved.workspaceId);

  if (Number.isNaN(workspaceId)) {
    return <div className="p-6 text-red-600">Invalid workspace id.</div>;
  }

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900">
      <Navbar workspaceId={workspaceId} />

      <main className="mx-auto max-w-4xl px-6 py-10">
        <div className="mb-8">
          <h1 className="text-3xl font-bold">Trade Import</h1>
          <p className="mt-2 text-slate-600">
            Add manual trades or CSV records for workspace {workspaceId}.
          </p>
        </div>

        <ImportForm workspaceId={workspaceId} />
      </main>
    </div>
  );
}