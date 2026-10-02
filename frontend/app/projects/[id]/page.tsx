export default async function ProjectDetailPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  return (
    <main className="p-6 text-slate-100">
      <div className="mx-auto max-w-5xl card p-8">
        <p className="text-sm uppercase tracking-[0.2em] text-slate-400">Project</p>
        <h1 className="mt-3 text-3xl font-bold">Project #{id}</h1>
        <p className="mt-4 text-slate-300">Files, analyses, and issue history will appear in this project detail view.</p>
      </div>
    </main>
  );
}
