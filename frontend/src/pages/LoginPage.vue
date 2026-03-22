<template>
  <div class="login-page">
    <div class="login-card">
      <h1>Sign in</h1>
      <form @submit.prevent="handleSubmit">
        <div class="field">
          <label for="username">Username</label>
          <input
            id="username"
            v-model="username"
            type="text"
            autocomplete="username"
            required
            class="input"
          />
        </div>
        <div class="field">
          <label for="password">Password</label>
          <input
            id="password"
            v-model="password"
            type="password"
            autocomplete="current-password"
            required
            class="input"
          />
        </div>
        <p v-if="errorMessage" class="error">{{ errorMessage }}</p>
        <button type="submit" :disabled="loading" class="btn-submit">
          Sign in
        </button>
      </form>
    </div>
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

<style scoped>
.login-page {
  padding: 0 var(--space-4);
}

.login-card {
  max-width: 360px;
  margin: var(--space-8) auto;
  background: var(--color-bg);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  padding: var(--space-6);
}

.login-card h1 {
  margin-top: 0;
}

.field {
  margin-bottom: var(--space-3);
}

.field label {
  display: block;
  margin-bottom: var(--space-1);
  font-size: var(--font-size-sm);
  color: var(--color-text);
}

.input {
  width: 100%;
  padding: var(--space-2) var(--space-3);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-sm);
  font-size: var(--font-size-base);
  box-sizing: border-box;
}

.error {
  color: var(--color-danger);
  font-size: var(--font-size-sm);
  margin: var(--space-2) 0;
}

.btn-submit {
  width: 100%;
  padding: var(--space-2) var(--space-3);
  background: var(--color-primary);
  color: white;
  border: none;
  border-radius: var(--radius-sm);
  font-size: var(--font-size-base);
  cursor: pointer;
}

.btn-submit:hover:not(:disabled) {
  background: var(--color-primary-dark);
}

.btn-submit:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}
</style>
