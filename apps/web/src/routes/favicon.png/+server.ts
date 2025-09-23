import { Buffer } from 'node:buffer';
import type { RequestHandler } from './$types';

const PNG_BASE64 = 'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVQIW2Nk+M+AAQACAgEAff1jNQAAAABJRU5ErkJggg==';

const CACHE_HEADERS = {
  'Cache-Control': 'public, max-age=86400, immutable'
} as const;

export const GET: RequestHandler = () => {
  const body = Buffer.from(PNG_BASE64, 'base64');

  return new Response(body, {
    headers: {
      'Content-Type': 'image/png',
      ...CACHE_HEADERS
    }
  });
};
