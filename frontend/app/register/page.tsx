'use client';

import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { FormEvent, useState } from 'react';

import { authenticate } from '@/lib/api';

export default function RegisterPage() {
  const router = useRouter();
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [submitting, setSubmitting] = useState(false);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError('');
    setSubmitting(true);
    try {
      await authenticate('register', { name, email, password });
      router.push('/analyze');
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : 'Unable to create your account.');
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <main className="flex min-h-screen items-center justify-center p-6">
      <div className="card w-full max-w-md p-8">
        <h1 className="text-2xl font-bold text-white">Create account</h1>
        <p className="mt-2 text-sm text-slate-400">Start securing and improving your code.</p>
        <form className="mt-6 space-y-4" onSubmit={handleSubmit}>
          <div>
            <label htmlFor="name" className="mb-2 block text-sm text-slate-300">Name</label>
            <input id="name" autoComplete="name" required minLength={2} maxLength={100} value={name} onChange={(event) => setName(event.target.value)} className="w-full rounded-lg border border-slate-700 bg-slate-950 px-3 py-2 text-slate-100" placeholder="Jane Doe" />
          </div>
          <div>
            <label htmlFor="email" className="mb-2 block text-sm text-slate-300">Email</label>
            <input id="email" type="email" autoComplete="email" required value={email} onChange={(event) => setEmail(event.target.value)} className="w-full rounded-lg border border-slate-700 bg-slate-950 px-3 py-2 text-slate-100" placeholder="you@example.com" />
          </div>
          <div>
            <label htmlFor="password" className="mb-2 block text-sm text-slate-300">Password</label>
            <input id="password" type="password" autoComplete="new-password" required minLength={8} maxLength={128} value={password} onChange={(event) => setPassword(event.target.value)} className="w-full rounded-lg border border-slate-700 bg-slate-950 px-3 py-2 text-slate-100" placeholder="At least 8 characters" />
          </div>
          {error && <p role="alert" className="rounded-lg border border-rose-400/30 bg-rose-400/10 px-3 py-2 text-sm text-rose-200">{error}</p>}
          <button disabled={submitting} type="submit" className="w-full rounded-lg bg-blue-600 px-4 py-2.5 font-medium text-white disabled:cursor-wait disabled:opacity-60">
            {submitting ? 'Creating account...' : 'Register'}
          </button>
        </form>
        <div className="mt-4 text-sm text-slate-400">
          Already have an account? <Link href="/login" className="text-blue-300">Log in</Link>
        </div>
      </div>
    </main>
  );
}
