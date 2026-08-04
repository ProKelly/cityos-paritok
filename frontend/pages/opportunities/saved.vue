<script setup lang="ts">
import { ref, onMounted } from 'vue';
import {
  BookmarkIcon,
  TrashIcon,
  BuildingOfficeIcon,
  MapPinIcon,
  CalendarIcon,
  ClockIcon,
  ArrowRightIcon,
  SparklesIcon,
  DocumentTextIcon,
  EyeIcon,
  XCircleIcon,
  FolderOpenIcon,
  CheckCircleIcon,
  ArrowPathIcon
} from '@heroicons/vue/24/outline';

const api = useApi();
const saved = ref<any[]>([]);
const loading = ref(true);
const removing = ref<Set<string>>(new Set());
const error = ref("");

async function load() {
  loading.value = true;
  error.value = "";
  try {
    saved.value = await api.get("/opportunities/saved/list");
  } catch (e: any) {
    error.value = e?.data?.detail || "Couldn't load your saved opportunities.";
  } finally {
    loading.value = false;
  }
}
onMounted(load);

async function unsave(id: string) {
  removing.value.add(id);
  try {
    await api.del(`/opportunities/${id}/save`);
    saved.value = saved.value.filter((o) => o.id !== id);
  } catch (e) {
    // non-fatal - could show a toast notification
  } finally {
    removing.value.delete(id);
  }
}
</script>

<template>
  <div class="min-h-screen bg-navy-950 relative">
    <!-- Subtle Pattern Background -->
    <div class="absolute inset-0 pointer-events-none overflow-hidden opacity-[0.03]">
      <svg class="absolute inset-0 h-full w-full" xmlns="http://www.w3.org/2000/svg">
        <defs>
          <pattern id="grid" width="40" height="40" patternUnits="userSpaceOnUse">
            <path d="M 40 0 L 0 0 0 40" fill="none" stroke="#F2B84B" stroke-width="0.5"/>
          </pattern>
          <pattern id="dots" x="0" y="0" width="20" height="20" patternUnits="userSpaceOnUse">
            <circle cx="2" cy="2" r="1" fill="#4FD1C5" />
          </pattern>
        </defs>
        <rect width="100%" height="100%" fill="url(#grid)" />
        <rect width="100%" height="100%" fill="url(#dots)" />
      </svg>
    </div>

    <!-- Decorative Elements -->
    <div class="absolute inset-0 pointer-events-none">
      <div class="absolute top-1/4 -left-20 h-64 w-64 rounded-full bg-chart-400/5 blur-3xl"></div>
      <div class="absolute bottom-1/4 -right-20 h-64 w-64 rounded-full bg-signal-400/5 blur-3xl"></div>
    </div>

    <div class="absolute inset-0 pointer-events-none bg-[radial-gradient(ellipse_at_center,_transparent_0%,_#0A0E1A_100%)] opacity-60"></div>

    <AppNav />
    <main class="relative z-10 mx-auto max-w-4xl px-4 sm:px-6 py-8 sm:py-12">
      
      <!-- Header -->
      <div class="mb-8 pb-6 border-b border-navy-800/50">
        <div class="flex items-center gap-3 mb-2">
          <span class="inline-flex items-center gap-2 rounded-full bg-chart-400/10 px-3 py-1 text-xs font-mono text-chart-400 border border-chart-400/10">
            <BookmarkIcon class="h-3 w-3" />
            Your Shortlist
          </span>
        </div>
        <h1 class="text-2xl sm:text-3xl font-display font-medium text-parchment tracking-tight flex items-center gap-3">
          <FolderOpenIcon class="h-6 w-6 text-chart-400" />
          Saved Opportunities
        </h1>
        <p class="mt-1.5 text-sm text-navy-400">
          Track and manage opportunities you've saved for later.
        </p>
      </div>

      <!-- Loading State -->
      <div v-if="loading" class="flex flex-col items-center justify-center py-20">
        <ArrowPathIcon class="h-8 w-8 animate-spin text-chart-400" />
        <p class="mt-4 text-sm text-navy-500">Loading your saved opportunities...</p>
      </div>

      <!-- Error State -->
      <div v-else-if="error" class="rounded-xl bg-coral-400/5 border border-coral-400/20 p-5 flex items-start gap-3">
        <XCircleIcon class="h-5 w-5 text-coral-400 flex-shrink-0 mt-0.5" />
        <div>
          <p class="text-sm text-coral-400">{{ error }}</p>
          <button @click="load" class="mt-2 text-sm text-chart-400 hover:text-chart-300 transition-colors">
            Try again
          </button>
        </div>
      </div>

      <!-- Empty State -->
      <div v-else-if="!saved.length" class="text-center py-20">
        <div class="inline-flex h-20 w-20 items-center justify-center rounded-full bg-navy-800/30 border border-navy-700/50 mb-6">
          <BookmarkIcon class="h-10 w-10 text-navy-500" />
        </div>
        <h3 class="text-xl font-medium text-parchment">Nothing saved yet</h3>
        <p class="mt-2 text-sm text-navy-400 max-w-md mx-auto">
          Start exploring opportunities and save the ones that interest you. They'll appear here for easy access.
        </p>
        <NuxtLink to="/opportunities/find" class="inline-flex items-center gap-2 mt-6 rounded-lg bg-chart-400/10 px-5 py-2.5 text-sm font-medium text-chart-400 border border-chart-400/20 hover:bg-chart-400/20 transition-all">
          <SparklesIcon class="h-4 w-4" />
          Find opportunities
          <ArrowRightIcon class="h-4 w-4" />
        </NuxtLink>
      </div>

      <!-- Saved List -->
      <div v-else class="mt-6">
        <!-- Stats -->
        <div class="flex items-center justify-between mb-5">
          <p class="text-sm text-navy-400 flex items-center gap-2">
            <CheckCircleIcon class="h-4 w-4 text-chart-400" />
            <span>{{ saved.length }} saved opportunity{{ saved.length > 1 ? 's' : '' }}</span>
          </p>
          <button 
            @click="load" 
            class="text-xs text-navy-500 hover:text-parchment transition-colors inline-flex items-center gap-1"
          >
            <ArrowPathIcon class="h-3 w-3" />
            Refresh
          </button>
        </div>

        <ul class="space-y-4">
          <li v-for="o in saved" :key="o.id" class="group rounded-xl bg-navy-900/40 border border-navy-800/50 p-5 sm:p-6 backdrop-blur-sm transition-all hover:border-navy-700/70 hover:bg-navy-900/50">
            <div class="flex flex-col sm:flex-row sm:items-start gap-4">
              <!-- Content -->
              <div class="flex-1 min-w-0">
                <div class="flex items-center gap-2 flex-wrap">
                  <span class="inline-flex items-center gap-1 rounded-full bg-navy-800/50 px-2.5 py-0.5 text-xs font-mono text-navy-400 border border-navy-700/50">
                    <BuildingOfficeIcon class="h-3 w-3" />
                    {{ o.category || 'Opportunity' }}
                  </span>
                  <span v-if="o.deadline" class="inline-flex items-center gap-1 rounded-full bg-navy-800/50 px-2.5 py-0.5 text-xs font-mono text-navy-400 border border-navy-700/50">
                    <CalendarIcon class="h-3 w-3" />
                    {{ o.deadline }}
                  </span>
                  <span v-else class="inline-flex items-center gap-1 rounded-full bg-navy-800/50 px-2.5 py-0.5 text-xs font-mono text-navy-400 border border-navy-700/50">
                    <ClockIcon class="h-3 w-3" />
                    Rolling deadline
                  </span>
                </div>
                
                <NuxtLink :to="`/opportunities/${o.id}`" class="mt-2 block text-lg font-medium text-parchment hover:text-chart-400 transition-colors truncate">
                  {{ o.title }}
                </NuxtLink>
                
                <p class="text-sm text-navy-500 flex items-center gap-1.5">
                  <BuildingOfficeIcon class="h-3.5 w-3.5" />
                  {{ o.organization }}
                </p>

                <!-- Tags -->
                <div v-if="o.tags?.length" class="mt-3 flex flex-wrap gap-1.5">
                  <span v-for="tag in o.tags.slice(0, 3)" :key="tag" class="rounded-full bg-navy-800/30 px-2 py-0.5 text-[10px] text-navy-400 border border-navy-700/30">
                    {{ tag }}
                  </span>
                  <span v-if="o.tags.length > 3" class="rounded-full bg-navy-800/30 px-2 py-0.5 text-[10px] text-navy-400 border border-navy-700/30">
                    +{{ o.tags.length - 3 }} more
                  </span>
                </div>
              </div>

              <!-- Actions -->
              <div class="flex sm:flex-col items-center sm:items-end gap-2 shrink-0">
                <NuxtLink :to="`/opportunities/${o.id}`" class="inline-flex items-center gap-1.5 rounded-lg bg-navy-800/30 px-3.5 py-2 text-sm font-medium text-parchment border border-navy-700/50 hover:bg-navy-800/50 hover:border-navy-700/70 transition-all w-full sm:w-auto">
                  <EyeIcon class="h-4 w-4" />
                  <span class="hidden sm:inline">View</span>
                </NuxtLink>
                <button 
                  class="inline-flex items-center gap-1.5 rounded-lg bg-coral-400/5 px-3.5 py-2 text-sm font-medium text-coral-400 border border-coral-400/20 hover:bg-coral-400/10 transition-all w-full sm:w-auto disabled:opacity-50"
                  @click="unsave(o.id)"
                  :disabled="removing.has(o.id)"
                >
                  <TrashIcon v-if="!removing.has(o.id)" class="h-4 w-4" />
                  <ArrowPathIcon v-else class="h-4 w-4 animate-spin" />
                  <span class="hidden sm:inline">{{ removing.has(o.id) ? 'Removing...' : 'Remove' }}</span>
                </button>
              </div>
            </div>

            <!-- Saved timestamp -->
            <div class="mt-4 pt-4 border-t border-navy-800/50 flex items-center gap-2 text-xs text-navy-500">
              <BookmarkIcon class="h-3 w-3" />
              <span>Saved • {{ o.saved_at || 'Recently' }}</span>
            </div>
          </li>
        </ul>
      </div>
    </main>
  </div>
</template>