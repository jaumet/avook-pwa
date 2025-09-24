import { browser } from '$app/environment';

const API_PATH_PREFIX = '/api/';

function normalizeServerBase(rawBase: string | undefined): string {
  if (!rawBase) {
    return API_PATH_PREFIX;
  }

  try {
    const url = new URL(rawBase);
    const trimmedPath = url.pathname.replace(/\/+$/, '');

    if (trimmedPath === '' || trimmedPath === '/') {
      url.pathname = API_PATH_PREFIX;
    } else if (trimmedPath.endsWith('/api')) {
      url.pathname = `${trimmedPath}/`;
    } else {
      url.pathname = `${trimmedPath}/`;
    }

    return `${url.origin}${url.pathname}`;
  } catch {
    const normalized = rawBase.replace(/\/+$/, '');

    if (!normalized) {
      return API_PATH_PREFIX;
    }

    if (normalized === '/' || normalized === '.') {
      return API_PATH_PREFIX;
    }

    if (normalized.endsWith('/api')) {
      return `${normalized}/`;
    }

    return `${normalized}/`;
  }
}

const RAW_BASE = import.meta.env.VITE_API_BASE as string | undefined;
const SERVER_API_BASE = normalizeServerBase(RAW_BASE);

function resolveBrowserBase(): string {
  if (!browser) {
    return SERVER_API_BASE;
  }

  // When the configured base is absolute we reuse it in the browser so local
  // development (where Vite runs on port 5173) can still reach the API
  // container running on a different host/port. Deployments that rely on an
  // ingress proxy can continue to omit ``VITE_API_BASE`` to fall back to the
  // relative ``/api`` prefix.
  if (/^https?:\/\//i.test(SERVER_API_BASE)) {
    return SERVER_API_BASE;
  }

  return API_PATH_PREFIX;
}

const API_BASE = resolveBrowserBase();

export async function apiFetch<T>(
  endpoint: string,
  init: RequestInit = {},
  fetcher: typeof fetch = fetch
): Promise<T> {
  const trimmedEndpoint = endpoint.trim();
  const isAbsolute = /^https?:\/\//i.test(trimmedEndpoint);
  const endpointPath = isAbsolute ? trimmedEndpoint : trimmedEndpoint.replace(/^\/+/, '');
  const normalizedBase = API_BASE.endsWith('/') ? API_BASE : `${API_BASE}/`;
  const requestUrl = isAbsolute ? endpointPath : `${normalizedBase}${endpointPath}`;

  const response = await fetcher(requestUrl, {
    credentials: 'include',
    ...init,
    headers:
      init.headers instanceof Headers || Array.isArray(init.headers)
        ? init.headers
        : {
            'Content-Type': 'application/json',
            ...(init.headers ?? {})
          }
  });

  if (!response.ok) {
    throw new Error(`API request failed with status ${response.status}`);
  }

  return response.json() as Promise<T>;
}
