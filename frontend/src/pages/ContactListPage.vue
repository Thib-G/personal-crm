<template>
  <div class="page">
    <div class="page-header">
      <h1>Contacts</h1>
      <button type="button" class="btn-primary" @click="router.push('/contacts/new')">Add Contact</button>
    </div>

    <div>
      <input
        v-model="searchQuery"
        type="search"
        placeholder="Search contacts…"
        aria-label="Search contacts"
        class="search-input"
      />
    </div>

    <ul v-if="displayedContacts.length > 0" class="contact-list">
      <li
        v-for="contact in displayedContacts"
        :key="contact.id"
        class="contact-item"
        @click="router.push(`/contacts/${contact.id}`)"
      >
        <span class="contact-name">{{ contact.name }}</span>
        <div class="contact-meta">
          <span v-if="contact.organisation" class="contact-org">{{ contact.organisation }}</span>
          <span class="contact-tag">{{ contact.context_tag }}</span>
          <span class="contact-date">{{ formatDate(contact.created_at) }}</span>
        </div>
      </li>
    </ul>

    <div v-else class="empty-state">
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

<style scoped>
.page {
  padding: var(--space-4);
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--space-4);
}

.search-input {
  width: 100%;
  padding: var(--space-2) var(--space-3);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-sm);
  font-size: var(--font-size-base);
  box-sizing: border-box;
}

.contact-list {
  list-style: none;
  padding: 0;
  margin-top: var(--space-4);
}

.contact-item {
  cursor: pointer;
  padding: var(--space-3) var(--space-4);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  margin-bottom: var(--space-2);
  background: var(--color-bg);
}

.contact-item:hover {
  background: var(--color-bg-muted);
}

.contact-name {
  font-weight: 600;
  color: var(--color-text);
  display: block;
}

.contact-meta {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-2);
  margin-top: var(--space-1);
  align-items: center;
}

.contact-org {
  font-size: var(--font-size-sm);
  color: var(--color-text-muted);
}

.contact-tag {
  font-size: var(--font-size-sm);
  color: var(--color-tag-text);
  background: var(--color-tag-bg);
  border-radius: var(--radius-sm);
  padding: 2px var(--space-1);
}

.contact-date {
  font-size: var(--font-size-sm);
  color: var(--color-text-muted);
}

.empty-state {
  margin-top: var(--space-8);
  color: var(--color-text-muted);
  text-align: center;
}

.btn-primary {
  background: var(--color-primary);
  color: white;
  border: none;
  border-radius: var(--radius-sm);
  padding: var(--space-2) var(--space-4);
  font-size: var(--font-size-base);
  cursor: pointer;
}

.btn-primary:hover {
  background: var(--color-primary-dark);
}

@media (min-width: 960px) {
  .page {
    max-width: 960px;
    margin: 0 auto;
  }
}
</style>
