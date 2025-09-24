import { browser } from '$app/environment';

const API_PATH_PREFIX = '/api/';

function normalizeServerBase(): string {
  const rawBase = import.meta.env.VITE_API_BASE;

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

const SERVER_API_BASE = normalizeServerBase();
const API_BASE = browser ? API_PATH_PREFIX : SERVER_API_BASE;

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
