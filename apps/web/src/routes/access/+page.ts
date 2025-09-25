import type { PageLoad } from './$types';
import { normalizeToken, resolveAccessPage } from './resolve';

export const load: PageLoad = async ({ url, fetch }) => {
  const token = normalizeToken(url.searchParams.get('token'));

  return resolveAccessPage(token, fetch);
};

