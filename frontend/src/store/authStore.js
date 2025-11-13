import { create } from 'zustand';
import { persist } from 'zustand/middleware';

const useAuthStore = create(
  persist(
    (set, get) => ({
      // 상태
      user: null,
      isAuthenticated: false,

      // 액션
      setUser: (user) => set({ user, isAuthenticated: true }),

      logout: () => {
        set({ user: null, isAuthenticated: false });
        localStorage.removeItem('access_token');
      },

      isAdmin: () => {
        const { user } = get();
        return user?.role === 'admin';
      },
    }),
    {
      name: 'auth-storage',
      getStorage: () => localStorage,
    }
  )
);

export default useAuthStore;
