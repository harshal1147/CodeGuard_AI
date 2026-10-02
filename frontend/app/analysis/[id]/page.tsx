'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { useParams } from 'next/navigation';

import { AnalysisDetails, AnalysisIssue, getAnalysis, getStoredToken } from '@/lib/api';

export default function AnalysisDetailPage() {
  const params = useParams<{ id: string }>();
  const [analysis, setAnalysis] = useState<AnalysisDetails | null>(null);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const token = getStoredToken();
    if (!token) {
      setError('Sign in to view this analysis report.');
      setLoading(false);
      return;
    }

    let active = true;
    getAnalysis(token, params.id)
      .then((report) => { if (active) setAnalysis(report); })
      .catch((cause: unknown) => {
        if (active) setError(cause instanceof Error ? cause.message : 'Unable to load this report.');
      })
      .finally(() => { if (active) setLoading(false); });

    return () => { active = false; };
  }, [params.id]);

  return (
    <main className="p-6 text-slate-100">
      <div className="mx-auto max-w-7xl">
        <Link href="/history" className="text-sm text-blue-300 hover:text-blue-200">← Analysis history</Link>
        {loading && <p role="status" className="py-12 text-center text-slate-400">Loading report...</p>}
        {error && <p role="alert" className="mt-6 rounded-md border border-rose-400/30 bg-rose-400/10 p-4 text-sm text-rose-100">{error}</p>}
        {analysis && (
          <>
            <header className="mb-6 mt-5 flex flex-wrap items-end justify-between gap-4">
              <div>
                <p className="text-sm uppercase tracking-[0.16em] text-slate-400">{analysis.language} · {analysis.status}</p>
                <h1 className="mt-2 text-3xl font-bold">{analysis.result?.filename ?? 'Analysis report'}</h1>
              </div>
              <div className="text-right">
                <div className="text-sm text-slate-400">Quality score</div>
                <div className="mt-1 text-3xl font-semibold text-blue-300">{analysis.score ?? '—'}<span className="text-base text-slate-500"> / 100</span></div>
              </div>
            </header>

            {!analysis.result ? (
              <p className="rounded-md border border-slate-700 p-5 text-sm text-slate-300">This older analysis has no stored detailed report.</p>
            ) : (
              <>
                <section className="mb-6 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
                  <Metric label="Findings" value={String(analysis.findings_count)} />
                  <Metric label="Estimated time" value={analysis.result.metrics.estimated_time_complexity} />
                  <Metric label="Estimated space" value={analysis.result.metrics.estimated_space_complexity} />
                  <Metric label="Cyclomatic complexity" value={analysis.result.metrics.cyclomatic_complexity === null ? 'Unavailable' : `${analysis.result.metrics.cyclomatic_complexity} · ${analysis.result.metrics.cyclomatic_rating}`} />
                </section>

                <section className="grid gap-6 lg:grid-cols-[0.7fr_1.3fr]">
                  <div className="card p-5">
                    <h2 className="text-lg font-semibold">Quality breakdown</h2>
                    <div className="mt-5 space-y-4">
                      {Object.entries(analysis.result.metrics.quality_scores)
                        .filter(([key]) => key !== 'overall')
                        .map(([key, score]) => (
                          <div key={key}>
                            <div className="mb-1 flex justify-between text-sm capitalize text-slate-300"><span>{key}</span><span>{score}</span></div>
                            <div className="h-1.5 rounded bg-slate-800"><div className="h-1.5 rounded bg-blue-400" style={{ width: `${score}%` }} /></div>
                          </div>
                        ))}
                    </div>
                  </div>
                  <div className="card p-5">
                    <div className="flex items-center justify-between">
                      <h2 className="text-lg font-semibold">Findings</h2>
                      <time className="text-sm text-slate-400" dateTime={analysis.created_at}>{new Date(analysis.created_at).toLocaleString()}</time>
                    </div>
                    {analysis.result.issues.length ? (
                      <div className="mt-4 space-y-3">
                        {analysis.result.issues.map((issue, index) => <IssueRow key={`${issue.type}-${issue.line}-${index}`} issue={issue} />)}
                      </div>
                    ) : (
                      <p className="mt-5 rounded-md border border-emerald-400/20 bg-emerald-400/5 p-4 text-sm text-emerald-200">No findings were detected by the current rules.</p>
                    )}
                  </div>
                </section>
              </>
            )}
          </>
        )}
      </div>
    </main>
  );
}

function Metric({ label, value }: { label: string; value: string }) {
  return (
    <div className="card p-5">
      <div className="text-sm text-slate-400">{label}</div>
      <div className="mt-3 text-lg font-semibold text-white">{value}</div>
    </div>
  );
}

function IssueRow({ issue }: { issue: AnalysisIssue }) {
  const severityStyles: Record<AnalysisIssue['severity'], string> = {
    CRITICAL: 'bg-rose-500/15 text-rose-200',
    HIGH: 'bg-orange-500/15 text-orange-200',
    MEDIUM: 'bg-amber-500/15 text-amber-200',
    LOW: 'bg-sky-500/15 text-sky-200',
    INFO: 'bg-slate-700 text-slate-200',
  };

  return (
    <article className="rounded-lg border border-slate-700 bg-slate-950/50 p-4">
      <div className="flex flex-wrap items-center gap-2">
        <span className={`rounded px-2 py-1 text-[11px] font-semibold ${severityStyles[issue.severity]}`}>{issue.severity}</span>
        <h3 className="font-medium text-white">{issue.title}</h3>
        {issue.line !== null && <span className="text-xs text-slate-500">Line {issue.line}</span>}
      </div>
      <p className="mt-3 text-sm text-slate-300">{issue.message}</p>
      <p className="mt-2 text-sm text-slate-400"><span className="text-slate-300">Recommendation:</span> {issue.recommendation}</p>
      <div className="mt-3 flex gap-2 text-xs text-slate-500"><span className="capitalize">{issue.category}</span><span>·</span><span>{issue.confidence} confidence</span></div>
    </article>
  );
}
