import { init, register, getLocaleFromNavigator } from 'svelte-i18n';

register('ca', () => import('./ca.json'));
register('es', () => import('./es.json'));
register('en', () => import('./en.json'));

export function setupI18n(): void {
  init({
    fallbackLocale: 'en',
    initialLocale: getLocaleFromNavigator()
  });
}
