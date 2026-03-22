<template>
  <div>
    <nav v-if="!isLoginRoute" class="nav">
      <router-link to="/contacts">Contacts</router-link>
      <router-link to="/map">Map</router-link>
      <router-link to="/settings">Settings</router-link>
      <SyncStatusIcon class="nav-sync" />
      <button class="nav-logout" @click="handleLogout">Logout</button>
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

<style scoped>
.nav {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-2);
  align-items: center;
  padding: var(--space-2) var(--space-4);
  border-bottom: 1px solid var(--color-border);
  background: var(--color-bg);
}

.nav a {
  color: var(--color-text-muted);
  text-decoration: none;
  padding: var(--space-1) var(--space-2);
  border-radius: var(--radius-sm);
  min-height: 44px;
  display: flex;
  align-items: center;
}

.nav a:hover {
  color: var(--color-primary);
}

.nav a.router-link-active {
  color: var(--color-primary);
  font-weight: 600;
}

.nav-sync {
  margin-left: auto;
}

.nav-logout {
  color: var(--color-text-muted);
  background: none;
  border: none;
  cursor: pointer;
  padding: var(--space-1) var(--space-2);
  font-size: var(--font-size-base);
  min-height: 44px;
}

.nav-logout:hover {
  color: var(--color-primary);
}

@media (min-width: 960px) {
  .nav {
    max-width: 960px;
    margin: 0 auto;
  }
}
</style>
