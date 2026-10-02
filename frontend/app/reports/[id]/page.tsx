export default async function ReportPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  return (
    <main className="p-6 text-slate-100">
      <div className="mx-auto max-w-5xl card p-8">
        <p className="text-sm uppercase tracking-[0.2em] text-slate-400">Report</p>
        <h1 className="mt-3 text-3xl font-bold">Report #{id}</h1>
        <p className="mt-4 text-slate-300">The downloadable PDF report and summary sections live here.</p>
      </div>
    </main>
  );
}
