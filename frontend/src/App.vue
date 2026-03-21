<template>
  <div>
    <nav v-if="!isLoginRoute" style="padding: 8px 16px; border-bottom: 1px solid #ccc; display: flex; gap: 16px; align-items: center;">
      <router-link to="/contacts">Contacts</router-link>
      <router-link to="/map">Map</router-link>
      <router-link to="/settings">Settings</router-link>
      <SyncStatusIcon style="margin-left: auto;" />
      <button @click="handleLogout">Logout</button>
    </nav>
    <router-view />
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from './stores/auth'
import SyncStatusIcon from './components/SyncStatusIcon.vue'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

const isLoginRoute = computed(() => route.path === '/login')

async function handleLogout(): Promise<void> {
  await authStore.logout()
  await router.push('/login')
}
</script>
