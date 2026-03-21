<template>
  <div style="max-width: 360px; margin: 80px auto; padding: 0 16px;">
    <h1>Sign in</h1>
    <form @submit.prevent="handleSubmit">
      <div style="margin-bottom: 12px;">
        <label for="username">Username</label><br />
        <input
          id="username"
          v-model="username"
          type="text"
          autocomplete="username"
          required
          style="width: 100%; padding: 8px; box-sizing: border-box;"
        />
      </div>
      <div style="margin-bottom: 12px;">
        <label for="password">Password</label><br />
        <input
          id="password"
          v-model="password"
          type="password"
          autocomplete="current-password"
          required
          style="width: 100%; padding: 8px; box-sizing: border-box;"
        />
      </div>
      <p v-if="errorMessage" style="color: red;">{{ errorMessage }}</p>
      <button type="submit" :disabled="loading" style="padding: 8px 16px;">
        Sign in
      </button>
    </form>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const username = ref('')
const password = ref('')
const errorMessage = ref<string | null>(null)
const loading = ref(false)

async function handleSubmit(): Promise<void> {
  errorMessage.value = null
  loading.value = true

  try {
    await authStore.login(username.value, password.value)
    await router.push('/contacts')
  } catch (err) {
    if (err instanceof Error && err.message === 'Invalid username or password') {
      errorMessage.value = 'Invalid username or password'
    } else {
      errorMessage.value = 'An unexpected error occurred. Please try again.'
    }
  } finally {
    loading.value = false
  }
}
</script>
