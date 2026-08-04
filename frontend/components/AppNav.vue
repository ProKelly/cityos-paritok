<script setup lang="ts">
import { ref } from 'vue';

const { user, signOut } = useAuth();
const route = useRoute();
const isOpen = ref(false);

const links = [
  { to: "/dashboard", label: "Dashboard", icon: "grid" },
  { to: "/opportunities/find", label: "Find Opportunities", icon: "search" },
  { to: "/opportunities/saved", label: "Saved", icon: "bookmark" },
  { to: "/roadmap", label: "Roadmap", icon: "map" },
  { to: "/career-coach", label: "Career Coach", icon: "compass" },
  { to: "/career-chat", label: "Career Chat", icon: "chat" },
  { to: "/profile", label: "Profile", icon: "user" },
];
</script>

<template>
  <header class="sticky top-0 z-40 border-b border-navy-800/50 bg-navy-950/80 backdrop-blur-md">
    <nav class="mx-auto flex max-w-7xl items-center justify-between px-4 sm:px-6 py-3 sm:py-4">
      <!-- Left Section -->
      <div class="flex items-center gap-4">
        <!-- Mobile Menu Toggle -->
        <button 
          @click="isOpen = !isOpen" 
          class="text-navy-500 hover:text-parchment transition-colors md:hidden focus:outline-none p-1 -ml-1"
          aria-label="Toggle Menu"
        >
          <svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path v-if="!isOpen" stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M4 6h16M4 12h16M4 18h16" />
            <path v-else stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>

        <!-- Logo -->
        <NuxtLink to="/dashboard" class="flex items-center gap-2.5 group">
          <div class="flex h-8 w-8 items-center justify-center rounded-lg bg-navy-800/50 border border-navy-700/50 transition-colors group-hover:border-navy-600">
            <img src="/cityos.svg" alt="CityOS" class="h-4 w-auto object-contain" />
          </div>
          <div class="flex items-center gap-2">
            <span class="text-base font-display font-medium text-parchment tracking-tight">CityOS</span>
            <span class="rounded-full bg-chart-400/10 px-2 py-0.5 text-[9px] font-mono font-medium uppercase tracking-widest text-chart-400 border border-chart-400/10">AI</span>
          </div>
        </NuxtLink>
      </div>

      <!-- Desktop Navigation -->
      <ul class="hidden items-center gap-1 md:flex">
        <li v-for="link in links" :key="link.to">
          <NuxtLink
            :to="link.to"
            class="relative px-3.5 py-2 text-sm font-medium transition-all duration-200 rounded-lg"
            :class="[
              route.path.startsWith(link.to) 
                ? 'text-parchment bg-navy-800/30' 
                : 'text-navy-400 hover:text-parchment hover:bg-navy-800/20'
            ]"
          >
            {{ link.label }}
            <span 
              v-if="route.path.startsWith(link.to)" 
              class="absolute bottom-0 left-1/2 -translate-x-1/2 h-0.5 w-4 rounded-full bg-chart-400"
            ></span>
          </NuxtLink>
        </li>
      </ul>

      <!-- Right Section -->
      <div class="flex items-center gap-3">
        <ClientOnly>
          <div class="hidden sm:flex items-center gap-2.5">
            <div class="h-6 w-6 rounded-full bg-navy-800/50 border border-navy-700/50 flex items-center justify-center">
              <span class="text-xs font-medium text-parchment">
                {{ user?.email?.charAt(0)?.toUpperCase() || 'U' }}
              </span>
            </div>
            <span class="text-sm text-navy-400 truncate max-w-[120px]">
              {{ user?.email }}
            </span>
          </div>
        </ClientOnly>
        
        <button 
          @click="signOut" 
          class="rounded-lg px-4 py-2 text-sm font-medium text-navy-400 hover:text-parchment hover:bg-navy-800/30 transition-all duration-200 border border-transparent hover:border-navy-700/50"
        >
          Sign out
        </button>
      </div>
    </nav>

    <!-- Mobile Navigation Drawer -->
    <transition
      enter-active-class="transition-all duration-200 ease-out"
      enter-from-class="opacity-0 -translate-y-2"
      enter-to-class="opacity-100 translate-y-0"
      leave-active-class="transition-all duration-150 ease-in"
      leave-from-class="opacity-100 translate-y-0"
      leave-to-class="opacity-0 -translate-y-2"
    >
      <div v-if="isOpen" class="border-t border-navy-800/50 bg-navy-950/95 backdrop-blur-md px-4 py-3 md:hidden">
        <ul class="space-y-1">
          <li v-for="link in links" :key="link.to">
            <NuxtLink
              :to="link.to"
              @click="isOpen = false"
              class="block rounded-lg px-3.5 py-2.5 text-sm font-medium transition-colors"
              :class="[
                route.path.startsWith(link.to) 
                  ? 'text-parchment bg-navy-800/30' 
                  : 'text-navy-400 hover:text-parchment hover:bg-navy-800/20'
              ]"
            >
              {{ link.label }}
            </NuxtLink>
          </li>
          <li class="pt-2 mt-2 border-t border-navy-800/50">
            <ClientOnly>
              <div class="flex items-center gap-3 px-3.5 py-2">
                <div class="h-8 w-8 rounded-full bg-navy-800/50 border border-navy-700/50 flex items-center justify-center">
                  <span class="text-sm font-medium text-parchment">
                    {{ user?.email?.charAt(0)?.toUpperCase() || 'U' }}
                  </span>
                </div>
                <span class="text-sm text-navy-400 truncate">{{ user?.email }}</span>
              </div>
            </ClientOnly>
          </li>
        </ul>
      </div>
    </transition>
  </header>
</template>