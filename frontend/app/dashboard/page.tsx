import Link from 'next/link';

const metrics = [
  { label: 'Total analyses', value: '128', tone: 'blue' },
  { label: 'Critical issues', value: '12', tone: 'red' },
  { label: 'Security issues', value: '24', tone: 'amber' },
  { label: 'Average score', value: '84', tone: 'green' },
];

export default function DashboardPage() {
  return (
    <main className="p-6 text-slate-100">
      <div className="mx-auto max-w-7xl">
        <div className="mb-8 flex items-center justify-between">
          <div>
            <p className="text-sm uppercase tracking-[0.2em] text-slate-400">Overview</p>
            <h1 className="mt-2 text-3xl font-bold">Dashboard</h1>
          </div>
          <Link href="/analyze" className="rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white">Analyze code</Link>
        </div>

        <section className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
          {metrics.map(({ label, value, tone }) => (
            <div key={label} className="card p-5">
              <div className="text-sm text-slate-400">{label}</div>
              <div className={`mt-4 text-3xl font-semibold text-${tone}-400`}>{value}</div>
            </div>
          ))}
        </section>

        <section className="mt-8 grid gap-6 xl:grid-cols-[1.4fr_0.6fr]">
          <div className="card p-6">
            <h2 className="mb-4 text-lg font-semibold">Recent analyses</h2>
            <div className="space-y-3 text-sm text-slate-300">
              {['Python API', 'React dashboard', 'C++ parser', 'Java service'].map((item, index) => (
                <div key={item} className="flex items-center justify-between rounded-lg border border-slate-700 bg-slate-900/80 p-3">
                  <div>
                    <div className="font-medium text-white">{item}</div>
                    <div className="text-xs text-slate-400">{['Today', 'Yesterday', '2 days ago', 'Last week'][index]}</div>
                  </div>
                  <span className="rounded-full bg-emerald-500/15 px-2 py-1 text-xs text-emerald-300">{[88, 91, 76, 82][index]}/100</span>
                </div>
              ))}
            </div>
          </div>

          <div className="card p-6">
            <h2 className="mb-4 text-lg font-semibold">Languages</h2>
            <ul className="space-y-3 text-sm text-slate-300">
              {['Python', 'TypeScript', 'Java', 'C++'].map((lang, index) => (
                <li key={lang} className="flex items-center justify-between">
                  <span>{lang}</span>
                  <span>{[32, 28, 17, 12][index]}%</span>
                </li>
              ))}
            </ul>
          </div>
        </section>
      </div>
    </main>
  );
}
