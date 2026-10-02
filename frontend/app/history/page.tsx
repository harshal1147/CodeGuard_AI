'use client';

import { useEffect, useMemo, useState } from 'react';
import Link from 'next/link';

import { AnalysisHistoryItem, getAnalysisHistory, getStoredToken } from '@/lib/api';

const severityOptions = ['ALL', 'CRITICAL', 'HIGH', 'MEDIUM', 'LOW', 'INFO'] as const;

export default function HistoryPage() {
  const [history, setHistory] = useState<AnalysisHistoryItem[]>([]);
  const [search, setSearch] = useState('');
  const [language, setLanguage] = useState('ALL');
  const [severity, setSeverity] = useState<(typeof severityOptions)[number]>('ALL');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [needsLogin, setNeedsLogin] = useState(false);

  useEffect(() => {
    const token = getStoredToken();
    if (!token) {
      setNeedsLogin(true);
      setLoading(false);
      return;
    }

    let active = true;
    getAnalysisHistory(token)
      .then((items) => { if (active) setHistory(items); })
      .catch((cause: unknown) => {
        if (active) setError(cause instanceof Error ? cause.message : 'Unable to load analysis history.');
      })
      .finally(() => { if (active) setLoading(false); });

    return () => { active = false; };
  }, []);

  const languages = useMemo(() => Array.from(new Set(history.map((item) => item.language))), [history]);
  const visibleHistory = useMemo(() => {
    const query = search.trim().toLowerCase();
    return history.filter((item) => {
      const matchesSearch = !query || `${item.filename} ${item.project_name} ${item.language}`.toLowerCase().includes(query);
      const matchesLanguage = language === 'ALL' || item.language === language;
      const matchesSeverity = severity === 'ALL' || (item.severity_counts[severity] ?? 0) > 0;
      return matchesSearch && matchesLanguage && matchesSeverity;
    });
  }, [history, language, search, severity]);

  return (
    <main className="p-6 text-slate-100">
      <div className="mx-auto max-w-7xl">
        <div className="mb-6 flex flex-wrap items-end justify-between gap-4">
          <div>
            <p className="text-sm uppercase tracking-[0.16em] text-slate-400">Saved reports</p>
            <h1 className="mt-2 text-3xl font-bold">Analysis history</h1>
          </div>
          <span className="text-sm text-slate-400">{visibleHistory.length} analyses</span>
        </div>

        <div className="mb-4 flex flex-wrap gap-3">
          <input
            type="search"
            aria-label="Search analyses"
            placeholder="Search file or project"
            value={search}
            onChange={(event) => setSearch(event.target.value)}
            className="min-w-56 flex-1 rounded-md border border-slate-700 bg-slate-950 px-3 py-2 text-sm text-slate-100 placeholder:text-slate-500"
          />
          <select aria-label="Filter by language" value={language} onChange={(event) => setLanguage(event.target.value)} className="rounded-md border border-slate-700 bg-slate-950 px-3 py-2 text-sm text-slate-200">
            <option value="ALL">All languages</option>
            {languages.map((item) => <option key={item} value={item}>{item}</option>)}
          </select>
          <select aria-label="Filter by severity" value={severity} onChange={(event) => setSeverity(event.target.value as (typeof severityOptions)[number])} className="rounded-md border border-slate-700 bg-slate-950 px-3 py-2 text-sm text-slate-200">
            {severityOptions.map((item) => <option key={item} value={item}>{item === 'ALL' ? 'All severities' : item}</option>)}
          </select>
        </div>

        {needsLogin && <p role="alert" className="rounded-md border border-amber-400/30 bg-amber-400/10 p-4 text-sm text-amber-100">Sign in to view saved analyses. <Link href="/login" className="underline">Log in</Link>.</p>}
        {error && <p role="alert" className="rounded-md border border-rose-400/30 bg-rose-400/10 p-4 text-sm text-rose-100">{error}</p>}
        {loading ? (
          <p role="status" className="py-10 text-center text-sm text-slate-400">Loading analysis history...</p>
        ) : !needsLogin && !error && (
          <div className="overflow-x-auto rounded-lg border border-slate-800">
            <table className="w-full min-w-[760px] text-left text-sm text-slate-300">
              <thead className="bg-slate-900/80 text-xs uppercase tracking-wider text-slate-400">
                <tr>
                  <th className="px-4 py-3">Date</th>
                  <th className="px-4 py-3">File / project</th>
                  <th className="px-4 py-3">Language</th>
                  <th className="px-4 py-3">Score</th>
                  <th className="px-4 py-3">Findings</th>
                  <th className="px-4 py-3">Status</th>
                </tr>
              </thead>
              <tbody>
                {visibleHistory.map((item) => (
                  <tr key={item.id} className="border-t border-slate-800 transition-colors hover:bg-slate-900/60">
                    <td className="whitespace-nowrap px-4 py-4">{new Date(item.created_at).toLocaleString()}</td>
                    <td className="px-4 py-4">
                      <Link href={`/analysis/${item.id}`} className="font-medium text-blue-300 hover:text-blue-200">{item.filename}</Link>
                      <div className="mt-1 text-xs text-slate-500">{item.project_name}</div>
                    </td>
                    <td className="px-4 py-4 capitalize">{item.language}</td>
                    <td className="px-4 py-4 font-medium text-white">{item.score ?? '—'}</td>
                    <td className="px-4 py-4">
                      <span>{item.findings_count}</span>
                      {item.severity_counts.CRITICAL > 0 && <span className="ml-2 text-xs text-rose-300">{item.severity_counts.CRITICAL} critical</span>}
                    </td>
                    <td className="px-4 py-4 capitalize">{item.status}</td>
                  </tr>
                ))}
                {visibleHistory.length === 0 && (
                  <tr><td colSpan={6} className="px-4 py-12 text-center text-slate-400">{history.length ? 'No analyses match these filters.' : 'No saved analyses yet. Run an analysis to see it here.'}</td></tr>
                )}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </main>
  );
}
