// Global test setup
import { config } from '@vue/test-utils'
import { createPinia } from 'pinia'

// Install Pinia globally for tests
config.global.plugins = [createPinia()]
