type RouteContext = {
  params: Promise<{ path: string[] }>;
};

async function proxyToBackend(request: Request, context: RouteContext): Promise<Response> {
  const { path } = await context.params;
  const configuredBackend = process.env.BACKEND_URL ?? 'http://localhost:8000';
  const backendUrl = /^https?:\/\//i.test(configuredBackend)
    ? configuredBackend
    : `http://${configuredBackend}`;
  const targetUrl = new URL(`/api/${path.map(encodeURIComponent).join('/')}`, backendUrl);
  targetUrl.search = new URL(request.url).search;

  const headers = new Headers();
  for (const name of ['authorization', 'content-type', 'accept']) {
    const value = request.headers.get(name);
    if (value) headers.set(name, value);
  }

  const init: RequestInit = {
    method: request.method,
    headers,
    cache: 'no-store',
  };
  if (request.method !== 'GET' && request.method !== 'HEAD') {
    init.body = await request.arrayBuffer();
  }

  try {
    const upstream = await fetch(targetUrl, init);
    const responseHeaders = new Headers();
    for (const name of ['content-type', 'content-disposition', 'cache-control']) {
      const value = upstream.headers.get(name);
      if (value) responseHeaders.set(name, value);
    }
    return new Response(upstream.body, {
      status: upstream.status,
      headers: responseHeaders,
    });
  } catch {
    return Response.json({ detail: 'The analysis service is temporarily unavailable.' }, { status: 502 });
  }
}

export const GET = proxyToBackend;
export const POST = proxyToBackend;
export const DELETE = proxyToBackend;
