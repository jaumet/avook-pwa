import type { LayoutLoad } from './$types';
import { setupI18n } from '$lib/i18n';

export const load: LayoutLoad = async ({ fetch }) => {
  await setupI18n({ fetcher: fetch });

  return {};
};
