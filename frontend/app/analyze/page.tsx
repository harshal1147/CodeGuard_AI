'use client';

import { ChangeEvent, useRef, useState } from 'react';
import Link from 'next/link';
import { AlertTriangle, FileCode2, LoaderCircle, ScanSearch, Upload } from 'lucide-react';

import { CodeEditor } from '@/components/editor/CodeEditor';
import { AnalysisIssue, AnalysisReport, getOrCreateProject, getStoredToken, submitAnalysis } from '@/lib/api';

const sampleCode = `def calculate_total(items):
    total = 0
    for item in items:
        total += item
    return total
`;

const languageExtensions: Record<string, string> = {
  python: 'py',
  javascript: 'js',
  typescript: 'ts',
  java: 'java',
  c: 'c',
  cpp: 'cpp',
};

const uploadLanguages: Record<string, string> = {
  py: 'python',
  js: 'javascript',
  mjs: 'javascript',
  cjs: 'javascript',
  ts: 'typescript',
  java: 'java',
  c: 'c',
  h: 'c',
  cc: 'cpp',
  cpp: 'cpp',
  cxx: 'cpp',
  hh: 'cpp',
  hpp: 'cpp',
  hxx: 'cpp',
};

export default function AnalyzePage() {
  const [code, setCode] = useState(sampleCode);
  const [language, setLanguage] = useState('python');
  const [filename, setFilename] = useState('example.py');
  const [report, setReport] = useState<AnalysisReport | null>(null);
  const [error, setError] = useState('');
  const [needsLogin, setNeedsLogin] = useState(false);
  const [analyzing, setAnalyzing] = useState(false);
  const fileInput = useRef<HTMLInputElement>(null);

  async function handleAnalyze() {
    setError('');
    setNeedsLogin(false);
    setReport(null);
    if (!code.trim()) {
      setError('Enter code before starting the analysis.');
      return;
    }

    const token = getStoredToken();
    if (!token) {
      setNeedsLogin(true);
      return;
    }

    setAnalyzing(true);
    try {
      const project = await getOrCreateProject(token);
      const result = await submitAnalysis(token, {
        project_id: project.id,
        language,
        filename,
        code,
      });
      setReport(result);
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : 'Analysis could not be completed.');
      if (!getStoredToken()) setNeedsLogin(true);
    } finally {
      setAnalyzing(false);
    }
  }

  async function handleFileUpload(event: ChangeEvent<HTMLInputElement>) {
    const file = event.currentTarget.files?.[0];
    event.currentTarget.value = '';
    if (!file) return;
    const extension = file.name.toLowerCase().split('.').pop();
    const detectedLanguage = extension ? uploadLanguages[extension] : undefined;
    if (!detectedLanguage) {
      setError('Choose a supported Python, JavaScript, TypeScript, Java, C, or C++ source file.');
      return;
    }
    if (file.size > 5 * 1024 * 1024) {
      setError('The file is larger than the 5 MB analysis limit.');
      return;
    }

    setCode(await file.text());
    setFilename(file.name);
    setLanguage(detectedLanguage);
    setError('');
    setReport(null);
  }

  return (
    <main className="p-6 text-slate-100">
      <div className="mx-auto max-w-7xl">
        <div className="mb-6 flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
          <div>
            <p className="text-sm uppercase tracking-[0.2em] text-slate-400">Static analysis</p>
            <h1 className="mt-2 text-3xl font-bold">Analyze code</h1>
          </div>
          <div className="flex flex-wrap gap-2">
            <button
              type="button"
              onClick={handleAnalyze}
              disabled={analyzing || !code.trim()}
              className="inline-flex items-center justify-center gap-2 rounded-lg bg-blue-600 px-5 py-2.5 font-medium text-white disabled:cursor-not-allowed disabled:opacity-60"
            >
              {analyzing ? <LoaderCircle className="h-4 w-4 animate-spin" /> : <ScanSearch className="h-4 w-4" />}
              {analyzing ? 'Analyzing code...' : 'Analyze Code'}
            </button>
          </div>
        </div>

        <div className="card p-4">
          <div className="mb-4 flex flex-wrap items-center justify-between gap-3">
            <div className="flex items-center gap-2 text-sm text-slate-300">
              <FileCode2 className="h-4 w-4 text-blue-300" />
              <span>{filename}</span>
              <select
                aria-label="Programming language"
                value={language}
                onChange={(event) => {
                  const nextLanguage = event.target.value;
                  setLanguage(nextLanguage);
                  setFilename((current) => `${current.replace(/\.[^/.]+$/, '')}.${languageExtensions[nextLanguage]}`);
                  setReport(null);
                }}
                className="rounded border border-slate-700 bg-slate-900 px-2 py-1 text-xs text-slate-300"
              >
                <option value="python">Python</option>
                <option value="javascript">JavaScript</option>
                <option value="typescript">TypeScript</option>
                <option value="java">Java</option>
                <option value="c">C</option>
                <option value="cpp">C++</option>
              </select>
            </div>
            <div>
              <input ref={fileInput} type="file" accept=".py,.js,.mjs,.cjs,.ts,.java,.c,.h,.cc,.cpp,.cxx,.hh,.hpp,.hxx" className="sr-only" onChange={handleFileUpload} />
              <button
                type="button"
                onClick={() => fileInput.current?.click()}
                className="inline-flex items-center gap-2 rounded-md border border-slate-700 px-3 py-2 text-sm text-slate-200 hover:bg-slate-800"
              >
                <Upload className="h-4 w-4" />
                Upload source file
              </button>
            </div>
          </div>

          <CodeEditor value={code} language={language} onChange={(value) => { setCode(value); setReport(null); }} />
        </div>

        {needsLogin && (
          <p role="alert" className="mt-4 rounded-lg border border-amber-400/30 bg-amber-400/10 p-4 text-sm text-amber-100">
            Sign in before analyzing code. <Link href="/login" className="font-medium underline">Log in</Link> or <Link href="/register" className="font-medium underline">create an account</Link>.
          </p>
        )}
        {error && (
          <p role="alert" className="mt-4 flex items-start gap-2 rounded-lg border border-rose-400/30 bg-rose-400/10 p-4 text-sm text-rose-100">
            <AlertTriangle className="mt-0.5 h-4 w-4 shrink-0" />
            {error}
          </p>
        )}

        {report && (
          <section aria-live="polite" className="mt-8 space-y-6">
            <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
              <Metric label="Quality score" value={`${report.score ?? 0}/100`} tone="text-blue-300" />
              <Metric label="Findings" value={String(report.findings_count)} tone="text-white" />
              <Metric label="Estimated time" value={report.result.metrics.estimated_time_complexity} tone="text-amber-300" />
              <Metric label="Estimated space" value={report.result.metrics.estimated_space_complexity} tone="text-emerald-300" />
            </div>

            <div className="grid gap-6 lg:grid-cols-[0.7fr_1.3fr]">
              <section className="card p-5">
                <h2 className="text-lg font-semibold">Quality breakdown</h2>
                <p className="mt-1 text-xs text-slate-400">Rule-based score from detected findings</p>
                <div className="mt-5 space-y-4">
                  {Object.entries(report.result.metrics.quality_scores)
                    .filter(([key]) => key !== 'overall')
                    .map(([key, score]) => (
                      <div key={key}>
                        <div className="mb-1 flex justify-between text-sm capitalize text-slate-300">
                          <span>{key}</span><span>{score}</span>
                        </div>
                        <div className="h-1.5 rounded bg-slate-800">
                          <div className="h-1.5 rounded bg-blue-400" style={{ width: `${score}%` }} />
                        </div>
                      </div>
                    ))}
                </div>
                <div className="mt-5 border-t border-slate-700 pt-4 text-sm text-slate-300">
                  Cyclomatic complexity: <strong className="text-white">{report.result.metrics.cyclomatic_complexity ?? 'Unavailable'}</strong>
                  <span className="ml-2 text-slate-400">({report.result.metrics.cyclomatic_rating})</span>
                </div>
              </section>

              <section className="card p-5">
                <div className="flex items-center justify-between gap-3">
                  <div>
                    <h2 className="text-lg font-semibold">Findings</h2>
                    <p className="mt-1 text-xs text-slate-400">{report.result.filename} · heuristic complexity estimates</p>
                  </div>
                  <span className="rounded-full bg-slate-800 px-3 py-1 text-xs text-slate-300">{report.status}</span>
                </div>
                {report.result.issues.length === 0 ? (
                  <p className="mt-6 rounded-lg border border-emerald-400/20 bg-emerald-400/5 p-4 text-sm text-emerald-200">No findings detected by the current rules.</p>
                ) : (
                  <div className="mt-4 space-y-3">
                    {report.result.issues.map((issue, index) => <IssueRow key={`${issue.type}-${issue.line}-${index}`} issue={issue} />)}
                  </div>
                )}
              </section>
            </div>
          </section>
        )}
      </div>
    </main>
  );
}

function Metric({ label, value, tone }: { label: string; value: string; tone: string }) {
  return (
    <div className="card p-5">
      <div className="text-sm text-slate-400">{label}</div>
      <div className={`mt-3 text-2xl font-semibold ${tone}`}>{value}</div>
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
      <div className="mt-3 flex gap-2 text-xs text-slate-500">
        <span className="capitalize">{issue.category}</span>
        <span>·</span>
        <span>{issue.confidence} confidence</span>
      </div>
    </article>
  );
}
