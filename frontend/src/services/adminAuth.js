import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import axios from 'axios';

const useAdminAuthStore = create(
  persist(
    (set) => ({
      token: null,
      user: null,
      login: async (email, password) => {
        const response = await axios.post('/api/v1/admin/login', {
          username: email,
          password: password,
        }, {
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
