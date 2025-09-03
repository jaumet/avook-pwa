import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import api from './api';

const useAdminAuthStore = create(
  persist(
    (set) => ({
      token: null,
      user: null,
      login: async (email, password) => {
        const params = new URLSearchParams();
        params.append('username', email);
        params.append('password', password);

        const response = await api.post('/api/v1/admin/login', params, {
          headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
        });
        const { access_token } = response.data;
        set({ token: access_token });
        // You might want to fetch user details here and set the user
      },
      logout: () => set({ token: null, user: null }),
    }),
    {
      name: 'admin-auth-storage', // name of the item in the storage (must be unique)
    }
  )
);

export default useAdminAuthStore;
