const API_BASE = import.meta.env.VITE_API_BASE ?? '/api';

export async function apiFetch<T>(
  endpoint: string,
  init: RequestInit = {},
  fetcher: typeof fetch = fetch
): Promise<T> {
  const response = await fetcher(`${API_BASE}${endpoint}`, {
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
