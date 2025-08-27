import { get, set } from 'idb-keyval';

const DEVICE_ID_KEY = 'avook-device-id';

/**
 * Gets the unique device ID.
 * If it doesn't exist, it creates one and stores it in IndexedDB.
 * @returns {Promise<string>} The unique device ID.
 */
export const getDeviceId = async () => {
  let deviceId = await get(DEVICE_ID_KEY);

  if (!deviceId) {
    // Use Crypto.randomUUID() for a secure, unique identifier
    deviceId = crypto.randomUUID();
    await set(DEVICE_ID_KEY, deviceId);
  }

  return deviceId;
};
