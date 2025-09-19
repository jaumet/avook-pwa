import { apiFetch } from '$lib/api';
import type { PageLoad } from './$types';

const DEMO_TOKENS = ['DEMO-ALPHA', 'DEMO-BETA', 'DEMO-GAMMA'] as const;

type AccessStatus = 'new' | 'registered' | 'invalid' | 'blocked';

export type AccessValidation = {
  status: AccessStatus;
  can_reregister: boolean;
  preview_available: boolean;
  cooldown_until: string | null;
  product: { id: number | null; title: string | null } | null;
  token: string;
};

export interface AccessPageData {
  token: string | null;
  tokenStatus: AccessStatus | 'missing' | 'error';
  validation: AccessValidation | null;
  error: string | null;
  demoTokens: readonly string[];
}

export const load: PageLoad = async ({ url, fetch }) => {
  const token = url.searchParams.get('token')?.trim() ?? null;

  if (!token) {
    return {
      token,
      tokenStatus: 'missing',
      validation: null,
      error: null,
      demoTokens: DEMO_TOKENS
    } satisfies AccessPageData;
  }

  try {
    const payload = await apiFetch<AccessValidation>(
      '/access/validate',
      {
        method: 'POST',
        body: JSON.stringify({ token })
      },
      fetch
    );

    if (!payload?.status) {
      const errorMessage = 'Unknown validation response';

      return {
        token,
        tokenStatus: 'error',
        validation: null,
        error: errorMessage,
        demoTokens: DEMO_TOKENS
      } satisfies AccessPageData;
    }

    return {
      token,
      tokenStatus: payload.status,
      validation: payload,
      error: null,
      demoTokens: DEMO_TOKENS
    } satisfies AccessPageData;
  } catch (error) {
    const message = error instanceof Error ? error.message : 'Unknown error';
    return {
      token,
      tokenStatus: 'error',
      validation: null,
      error: message,
      demoTokens: DEMO_TOKENS
    } satisfies AccessPageData;
  }
};
