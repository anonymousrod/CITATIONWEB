// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
  // Ajout des modules
  modules: ['@nuxtjs/@pinia/nuxt'],
  devtools: { enabled: true },
  
  // Configuration pour le fichier .env
  runtimeConfig: {
    public: {
      backendUrl: process.env.NUXT_PUBLIC_BACKEND_URL || 'http://localhost:8000',
    },
  },

  // Configuration Pinia
  pinia: {
    storesDirs: ['./stores/**'],
  },

  // Nitro configuration
  nitro: {
    compatibilityDate: '2025-09-28'
  },
})