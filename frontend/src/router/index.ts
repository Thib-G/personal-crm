import { createRouter, createWebHistory, type RouteLocationNormalized } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      redirect: '/contacts',
    },
    {
      path: '/login',
      name: 'login',
      component: () => import('../pages/LoginPage.vue'),
    },
    {
      path: '/contacts',
      name: 'contacts',
      component: () => import('../pages/ContactListPage.vue'),
    },
    {
      path: '/contacts/new',
      name: 'contacts-new',
      component: () => import('../pages/AddContactPage.vue'),
    },
    {
      path: '/contacts/:id',
      name: 'contact-detail',
      component: () => import('../pages/ContactDetailPage.vue'),
    },
    {
      path: '/contacts/:id/edit',
      name: 'contact-edit',
      component: () => import('../pages/EditContactPage.vue'),
    },
    {
      path: '/map',
      name: 'map',
      component: () => import('../pages/MapPage.vue'),
    },
    {
      path: '/settings',
      name: 'settings',
      component: () => import('../pages/SettingsPage.vue'),
    },
  ],
})

router.beforeEach(async (to: RouteLocationNormalized) => {
  if (to.name === 'login') {
    return true
  }

  const authStore = useAuthStore()

  if (!authStore.user) {
    await authStore.checkSession()
  }

  if (!authStore.user) {
    return { name: 'login' }
  }

  return true
})

export default router
