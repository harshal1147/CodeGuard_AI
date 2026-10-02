export default function ProjectsPage() {
  return (
    <main className="p-6 text-slate-100">
      <div className="mx-auto max-w-7xl">
        <h1 className="text-3xl font-bold">Projects</h1>
        <div className="mt-6 grid gap-6 md:grid-cols-3">
          {['College E-Commerce App', 'Internal Analytics', 'Payments Gateway'].map((name) => (
            <div key={name} className="card p-5">
              <h2 className="text-xl font-semibold">{name}</h2>
              <p className="mt-3 text-sm text-slate-300">Project overview and analysis metrics will appear here.</p>
            </div>
          ))}
        </div>
      </div>
    </main>
  );
}
