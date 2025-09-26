import { getLocaleFromNavigator, init, register, waitLocale } from 'svelte-i18n';

const LOCALES = ['en', 'es', 'ca'] as const;
const TRANSLATION_BASE_PATH = '/locales';
const TRANSLATION_FILENAME = 'translation.json';
const FALLBACK_LOCALE = 'en';

type SupportedLocale = (typeof LOCALES)[number];

type LoaderResponse = Record<string, unknown>;

type Fetcher = (input: RequestInfo | URL, init?: RequestInit) => Promise<Response>;

let loaderFetch: Fetcher | null = typeof fetch === 'function' ? fetch : null;

function isSupportedLocale(locale: string): locale is SupportedLocale {
  return LOCALES.includes(locale as SupportedLocale);
}

function coerceLocale(locale: string | null | undefined): SupportedLocale {
  if (!locale) {
    return FALLBACK_LOCALE;
  }

  const normalized = locale.trim().toLowerCase().replace('_', '-');

  if (isSupportedLocale(normalized)) {
    return normalized;
  }

  const base = normalized.split('-')[0];

  if (isSupportedLocale(base)) {
    return base;
  }

  return FALLBACK_LOCALE;
}

function requireFetch(): Fetcher {
  if (!loaderFetch) {
    throw new Error('No fetch implementation available for loading translations');
  }

  return loaderFetch;
}

function createLoader(locale: SupportedLocale) {
  return async (): Promise<LoaderResponse> => {
    const response = await requireFetch()(
      `${TRANSLATION_BASE_PATH}/${locale}/${TRANSLATION_FILENAME}`
    );

    if (!response.ok) {
      throw new Error(`Failed to load translations for locale "${locale}"`);
    }

    return response.json();
  };
}

for (const locale of LOCALES) {
  register(locale, createLoader(locale));
}

export interface I18nSetupOptions {
  initialLocale?: string;
  fetcher?: Fetcher;
}

export async function setupI18n(options: I18nSetupOptions = {}): Promise<void> {
  if (options.fetcher) {
    loaderFetch = options.fetcher;
  }

  const resolvedLocale = options.initialLocale
    ? coerceLocale(options.initialLocale)
    : typeof navigator !== 'undefined'
      ? coerceLocale(getLocaleFromNavigator())
      : FALLBACK_LOCALE;

  init({
    fallbackLocale: FALLBACK_LOCALE,
    initialLocale: resolvedLocale
  });

  await waitLocale();
}

export { LOCALES as SUPPORTED_LOCALES };
