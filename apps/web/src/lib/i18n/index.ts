import { getLocaleFromNavigator, init, register } from 'svelte-i18n';

const LOCALES = ['en', 'es', 'ca'] as const;
const TRANSLATION_BASE_PATH = '/locales';
const TRANSLATION_FILENAME = 'translation.json';
const FALLBACK_LOCALE = 'en';

type SupportedLocale = (typeof LOCALES)[number];

type LoaderResponse = Record<string, unknown>;

function createLoader(locale: SupportedLocale) {
  return async (): Promise<LoaderResponse> => {
    const response = await fetch(
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

export function setupI18n(initialLocale?: string): void {
  const resolvedLocale =
    initialLocale ??
    (typeof navigator !== 'undefined' ? getLocaleFromNavigator() ?? FALLBACK_LOCALE : FALLBACK_LOCALE);

  init({
    fallbackLocale: FALLBACK_LOCALE,
    initialLocale: resolvedLocale
  });
}

export { LOCALES as SUPPORTED_LOCALES };
