import Link from 'next/link';

const featureList = [
  'Static analysis and bug detection',
  'Security scanning and secret masking',
  'Complexity and quality scoring',
  'AI review and improved code suggestions',
];

export default function HomePage() {
  return (
    <main className="min-h-screen text-slate-100">
      <section className="mx-auto grid max-w-7xl gap-12 px-6 py-16 lg:grid-cols-2 lg:items-center">
        <div>
          <span className="inline-flex rounded-full border border-blue-400/40 bg-blue-500/10 px-3 py-1 text-xs font-medium uppercase tracking-[0.2em] text-blue-200">
            Developer-first analysis
          </span>
          <h1 className="mt-6 text-4xl font-bold leading-tight text-white md:text-6xl">
            Write Better Code. Find Bugs Before They Find You.
          </h1>
          <p className="mt-6 max-w-xl text-lg text-slate-300">
            CodeGuard AI combines static analysis, security scanning, complexity analysis, and AI-powered code review into one platform built for modern engineering teams.
          </p>
          <div className="mt-8 flex flex-wrap gap-4">
            <Link href="/analyze" className="rounded-xl bg-blue-600 px-6 py-3 font-medium text-white shadow-glow">Start Analyzing</Link>
            <Link href="/dashboard" className="rounded-xl border border-slate-700 px-6 py-3 font-medium text-slate-100">View Demo</Link>
          </div>
          <ul className="mt-8 space-y-3 text-sm text-slate-300">
            {featureList.map((feature) => (
              <li key={feature} className="flex items-center gap-3">
                <span className="inline-block h-2.5 w-2.5 rounded-full bg-emerald-400" />
                {feature}
              </li>
            ))}
          </ul>
        </div>

        <div className="card grid-pattern min-h-[420px] p-6">
          <div className="rounded-2xl border border-slate-700 bg-slate-950/80 p-5">
            <div className="mb-4 flex items-center justify-between text-xs text-slate-400">
              <span>analysis-report.json</span>
              <span>84/100</span>
            </div>
            <div className="space-y-4 text-sm">
              <div className="rounded-lg border border-slate-700 bg-slate-900 p-3">
                <div className="mb-2 flex justify-between"><span>Security</span><span className="text-emerald-400">82</span></div>
                <div className="h-2 rounded bg-slate-800"><div className="h-2 w-[82%] rounded bg-emerald-400" /></div>
              </div>
              <div className="rounded-lg border border-slate-700 bg-slate-900 p-3">
                <div className="mb-2 flex justify-between"><span>Correctness</span><span className="text-blue-400">90</span></div>
                <div className="h-2 rounded bg-slate-800"><div className="h-2 w-[90%] rounded bg-blue-400" /></div>
              </div>
              <div className="rounded-lg border border-slate-700 bg-slate-900 p-3">
                <div className="mb-2 flex justify-between"><span>Maintainability</span><span className="text-amber-400">75</span></div>
                <div className="h-2 rounded bg-slate-800"><div className="h-2 w-[75%] rounded bg-amber-400" /></div>
              </div>
            </div>
          </div>
        </div>
      </section>

      <section id="features" className="mx-auto max-w-7xl px-6 py-16">
        <h2 className="text-3xl font-bold text-white">Everything you need to review code confidently</h2>
        <div className="mt-8 grid gap-6 md:grid-cols-3">
          {['Bug detection', 'Security review', 'AI recommendations'].map((title, index) => (
            <div key={title} className="card p-6">
              <div className="mb-4 h-12 w-12 rounded-xl bg-blue-500/10 text-lg text-blue-300">0{index + 1}</div>
              <h3 className="mb-2 text-xl font-semibold">{title}</h3>
              <p className="text-slate-300">Designed to catch the issues developers usually miss and explain them clearly in a code-review context.</p>
            </div>
          ))}
        </div>
      </section>
    </main>
  );
}
