<template>
  <div>
    <div style="display: flex; justify-content: space-between; align-items: center;">
      <h1>Contacts</h1>
      <button type="button" @click="router.push('/contacts/new')">Add Contact</button>
    </div>

    <div>
      <input
        v-model="searchQuery"
        type="search"
        placeholder="Search contacts…"
        aria-label="Search contacts"
      />
    </div>

    <ul v-if="displayedContacts.length > 0" style="list-style: none; padding: 0; margin-top: 16px;">
      <li
        v-for="contact in displayedContacts"
        :key="contact.id"
        style="cursor: pointer; padding: 8px 0; border-bottom: 1px solid #eee;"
        @click="router.push(`/contacts/${contact.id}`)"
      >
        <span style="font-weight: bold;">{{ contact.name }}</span>
        <span style="margin-left: 8px; font-size: 0.8em; background: #eee; padding: 2px 6px; border-radius: 4px;">
          {{ contact.context_tag }}
        </span>
        <span style="margin-left: 8px; font-size: 0.85em; color: #666;">
          {{ formatDate(contact.created_at) }}
        </span>
      </li>
    </ul>

    <div v-else style="margin-top: 32px; color: #666;">
      No contacts yet
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useContactStore } from '@/stores/contacts'
import type { Contact } from '@/services/db'

const router = useRouter()
const contactStore = useContactStore()

const searchQuery = ref('')
const apiResults = ref<Contact[]>([])
let debounceTimer: ReturnType<typeof setTimeout> | null = null

onMounted(async () => {
  await contactStore.loadContacts()
})

watch(searchQuery, (newQuery) => {
  if (debounceTimer) clearTimeout(debounceTimer)

  if (!newQuery.trim()) {
    apiResults.value = []
    return
  }

  debounceTimer = setTimeout(async () => {
    if (newQuery.trim().length >= 2) {
      await fetchFromApi(newQuery.trim())
    } else {
      apiResults.value = []
    }
  }, 300)
})

async function fetchFromApi(query: string) {
  try {
    const response = await fetch(`/api/contacts/?q=${encodeURIComponent(query)}`)
    if (!response.ok) throw new Error(`HTTP ${response.status}`)
    const data = await response.json()
    apiResults.value = Array.isArray(data) ? data : (data.results ?? [])
  } catch {
    apiResults.value = []
  }
}

const displayedContacts = computed<Contact[]>(() => {
  if (searchQuery.value.trim().length >= 2) {
    return apiResults.value
  }
  return contactStore.contacts
})

function formatDate(isoString: string): string {
  if (!isoString) return ''
  const date = new Date(isoString)
  return date.toLocaleDateString(undefined, { year: 'numeric', month: 'short', day: 'numeric' })
}
</script>
