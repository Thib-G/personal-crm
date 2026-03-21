import { defineStore } from 'pinia'
import { ref } from 'vue'

interface User {
  id: number
  username: string
}

export const useAuthStore = defineStore('auth', () => {
  const user = ref<User | null>(null)

  async function checkSession(): Promise<void> {
    try {
      const response = await fetch('/api/auth/me/')
      if (response.ok) {
        const data = (await response.json()) as User
        user.value = data
      } else {
        user.value = null
      }
    } catch {
      user.value = null
    }
  }

  async function login(username: string, password: string): Promise<void> {
    const response = await fetch('/api/auth/login/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, password }),
    })

    if (response.status === 401) {
      throw new Error('Invalid username or password')
    }

    if (!response.ok) {
      throw new Error('Login failed')
    }

    const data = (await response.json()) as User
    user.value = data
  }

  async function logout(): Promise<void> {
    await fetch('/api/auth/logout/', { method: 'POST' })
    user.value = null
  }

  return { user, checkSession, login, logout }
})
