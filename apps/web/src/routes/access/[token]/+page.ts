import type { PageLoad } from './$types';
import { normalizeToken, resolveAccessPage } from '../resolve';

export const load: PageLoad = async ({ params, fetch }) => {
  const token = normalizeToken(params.token);

  return resolveAccessPage(token, fetch);
};

