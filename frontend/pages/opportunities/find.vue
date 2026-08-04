<script setup lang="ts">
import { ref } from 'vue';
import {
  SparklesIcon,
  MagnifyingGlassIcon,
  ArrowPathIcon,
  BookmarkIcon,
  BookmarkSlashIcon,
  ArrowRightIcon,
  BuildingOfficeIcon,
  MapPinIcon,
  ChartBarIcon,
  LightBulbIcon,
  XCircleIcon,
  CheckCircleIcon,
  ClockIcon,
  AcademicCapIcon,
  RocketLaunchIcon,
  DocumentTextIcon,
  UserGroupIcon
} from '@heroicons/vue/24/outline';

const api = useApi();
const matches = ref<any[]>([]);
const loading = ref(false);
const error = ref("");
const hasSearched = ref(false);
const savedOpportunities = ref<Set<string>>(new Set());

async function findOpportunities() {
  loading.value = true;
  error.value = "";
  try {
    const res: any = await api.post("/recommend");
    matches.value = res.matches;
    hasSearched.value = true;
  } catch (e: any) {
    error.value = e?.data?.detail || "Couldn't run the matching engine. Try again.";
  } finally {
    loading.value = false;
  }
}

async function saveOpportunity(id: string) {
  try {
    await api.post(`/opportunities/${id}/save`);
    if (savedOpportunities.value.has(id)) {
      savedOpportunities.value.delete(id);
    } else {
      savedOpportunities.value.add(id);
    }
  } catch (e) {
    // non-fatal
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
    <main class="relative z-10 mx-auto max-w-5xl px-4 sm:px-6 py-8 sm:py-12">
      
      <!-- Header -->
      <div class="mb-8 pb-6 border-b border-navy-800/50">
        <div class="flex items-center gap-3 mb-2">
          <span class="inline-flex items-center gap-2 rounded-full bg-chart-400/10 px-3 py-1 text-xs font-mono text-chart-400 border border-chart-400/10">
            <SparklesIcon class="h-3 w-3" />
            Phase 4
          </span>
          <span class="text-xs font-mono text-navy-500">·</span>
          <span class="text-xs font-mono text-navy-500">The Matching Engine</span>
        </div>
        <h1 class="text-2xl sm:text-3xl font-display font-medium text-parchment tracking-tight flex items-center gap-3">
          Find Opportunities
        </h1>
        <p class="mt-1.5 text-sm text-navy-400 max-w-2xl">
          We embed your profile, pull the closest opportunities by semantic search, then have the AI rank and explain the best fits.
        </p>
      </div>

      <!-- Search Section -->
      <div class="rounded-xl bg-navy-900/40 border border-navy-800/50 p-5 sm:p-6 backdrop-blur-sm transition-all hover:border-navy-700/70">
        <div class="flex flex-col sm:flex-row sm:items-center gap-4">
          <div class="flex-1">
            <p class="text-sm text-navy-400 flex items-center gap-2">
              <UserGroupIcon class="h-4 w-4" />
              <span>Your Opportunity DNA is ready to match</span>
            </p>
          </div>
          <button 
            class="inline-flex items-center justify-center gap-2 rounded-lg bg-chart-400/10 px-6 py-3 text-sm font-medium text-chart-400 border border-chart-400/20 hover:bg-chart-400/20 transition-all disabled:opacity-50 disabled:cursor-not-allowed sm:min-w-[200px]"
            :disabled="loading" 
            @click="findOpportunities"
          >
            <MagnifyingGlassIcon v-if="!loading" class="h-4 w-4" />
            <ArrowPathIcon v-else class="h-4 w-4 animate-spin" />
            {{ loading ? "Scanning..." : "Find Opportunities" }}
          </button>
        </div>

        <!-- Error -->
        <div v-if="error" class="mt-4 rounded-lg bg-coral-400/5 border border-coral-400/20 p-3 flex items-start gap-2.5">
          <XCircleIcon class="h-4 w-4 text-coral-400 flex-shrink-0 mt-0.5" />
          <p class="text-sm text-coral-400">{{ error }}</p>
        </div>
      </div>

      <!-- Results -->
      <div v-if="hasSearched && !loading" class="mt-10">
        <!-- Empty State -->
        <div v-if="!matches.length" class="text-center py-16">
          <div class="inline-flex h-16 w-16 items-center justify-center rounded-full bg-navy-800/30 border border-navy-700/50 mb-4">
            <DocumentTextIcon class="h-8 w-8 text-navy-500" />
          </div>
          <h3 class="text-lg font-medium text-parchment">No strong matches yet</h3>
          <p class="mt-2 text-sm text-navy-400 max-w-md mx-auto">
            Try broadening your profile's skills or interests. The matching engine works best with a complete Opportunity DNA.
          </p>
          <NuxtLink to="/profile" class="inline-flex items-center gap-2 mt-4 text-sm text-chart-400 hover:text-chart-300 transition-colors">
            <SparklesIcon class="h-4 w-4" />
            Enhance your profile
            <ArrowRightIcon class="h-3 w-3" />
          </NuxtLink>
        </div>

        <!-- Results List -->
        <div class="space-y-4">
          <div class="flex items-center justify-between mb-4">
            <p class="text-sm text-navy-400 flex items-center gap-2">
              <CheckCircleIcon class="h-4 w-4 text-chart-400" />
              <span>{{ matches.length }} opportunity{{ matches.length > 1 ? 's' : '' }} found</span>
            </p>
          </div>

          <ul class="space-y-5">
            <li v-for="m in matches" :key="m.opportunity_id" class="group rounded-xl bg-navy-900/40 border border-navy-800/50 p-5 sm:p-6 backdrop-blur-sm transition-all hover:border-navy-700/70 hover:bg-navy-900/50">
              <!-- Header -->
              <div class="flex flex-wrap items-start justify-between gap-4">
                <div class="flex-1 min-w-0">
                  <div class="flex items-center gap-2 flex-wrap">
                    <span class="inline-flex items-center gap-1 rounded-full bg-navy-800/50 px-2.5 py-0.5 text-xs font-mono text-navy-400 border border-navy-700/50">
                      <BuildingOfficeIcon class="h-3 w-3" />
                      {{ m.opportunity?.category || 'General' }}
                    </span>
                    <span class="inline-flex items-center gap-1 rounded-full bg-navy-800/50 px-2.5 py-0.5 text-xs font-mono text-navy-400 border border-navy-700/50">
                      <MapPinIcon class="h-3 w-3" />
                      {{ m.opportunity?.country || 'Remote' }}
                    </span>
                  </div>
                  <NuxtLink :to="`/opportunities/${m.opportunity_id}`" class="mt-2 block text-lg font-medium text-parchment hover:text-chart-400 transition-colors truncate">
                    {{ m.opportunity?.title }}
                  </NuxtLink>
                  <p class="text-sm text-navy-500">{{ m.opportunity?.organization }}</p>
                </div>
                <div class="shrink-0 text-right">
                  <div class="flex items-center gap-2">
                    <div class="relative">
                      <svg class="h-14 w-14 -rotate-90">
                        <circle cx="28" cy="28" r="24" fill="none" stroke="#1a1a2e" stroke-width="4"/>
                        <circle cx="28" cy="28" r="24" fill="none" stroke="#4FD1C5" stroke-width="4" 
                          :stroke-dasharray="`${(m.match_score / 100) * 150.8} 150.8`"
                          stroke-linecap="round"
                        />
                      </svg>
                      <span class="absolute inset-0 flex items-center justify-center text-sm font-mono font-semibold text-chart-400">
                        {{ m.match_score }}%
                      </span>
                    </div>
                  </div>
                </div>
              </div>

              <!-- Reason -->
              <div class="mt-4 p-3 rounded-lg bg-navy-950/50 border border-navy-800/50">
                <div class="flex items-start gap-2.5">
                  <LightBulbIcon class="h-4 w-4 text-chart-400 flex-shrink-0 mt-0.5" />
                  <p class="text-sm text-parchment">{{ m.reason }}</p>
                </div>
              </div>

              <!-- Missing Skill & Next Step -->
              <div class="mt-3 grid gap-3 sm:grid-cols-2">
                <div v-if="m.missing_skill" class="flex items-start gap-2 text-sm text-coral-400">
                  <XCircleIcon class="h-4 w-4 flex-shrink-0 mt-0.5" />
                  <span>Missing skill: <strong>{{ m.missing_skill }}</strong></span>
                </div>
                <div class="flex items-start gap-2 text-sm text-chart-400 sm:col-start-2 sm:justify-self-end" :class="{ 'sm:col-start-2': m.missing_skill }">
                  <ArrowRightIcon class="h-4 w-4 flex-shrink-0 mt-0.5" />
                  <span>Next step: {{ m.next_step }}</span>
                </div>
              </div>

              <!-- Actions -->
              <div class="mt-5 flex flex-wrap items-center gap-2 pt-4 border-t border-navy-800/50">
                <NuxtLink :to="`/opportunities/${m.opportunity_id}`" class="inline-flex items-center gap-1.5 rounded-lg bg-navy-800/30 px-4 py-2 text-sm font-medium text-parchment border border-navy-700/50 hover:bg-navy-800/50 hover:border-navy-700/70 transition-all">
                  <DocumentTextIcon class="h-4 w-4" />
                  View details
                </NuxtLink>
                <button 
                  class="inline-flex items-center gap-1.5 rounded-lg bg-navy-800/30 px-4 py-2 text-sm font-medium text-parchment border border-navy-700/50 hover:bg-navy-800/50 hover:border-navy-700/70 transition-all"
                  @click="saveOpportunity(m.opportunity_id)"
                >
                  <BookmarkIcon v-if="!savedOpportunities.has(m.opportunity_id)" class="h-4 w-4" />
                  <BookmarkSlashIcon v-else class="h-4 w-4" />
                  {{ savedOpportunities.has(m.opportunity_id) ? 'Saved' : 'Save' }}
                </button>
                <NuxtLink :to="`/career-coach?opportunity_id=${m.opportunity_id}`" class="inline-flex items-center gap-1.5 rounded-lg bg-chart-400/10 px-4 py-2 text-sm font-medium text-chart-400 border border-chart-400/20 hover:bg-chart-400/20 transition-all">
                  <SparklesIcon class="h-4 w-4" />
                  Prepare me
                </NuxtLink>
                <span class="ml-auto text-xs text-navy-500 flex items-center gap-1">
                  <ClockIcon class="h-3 w-3" />
                  {{ m.opportunity?.deadline || 'No deadline' }}
                </span>
              </div>
            </li>
          </ul>
        </div>
      </div>

      <!-- Initial State (before search) -->
      <div v-if="!hasSearched && !loading" class="mt-10 text-center py-16">
        <div class="inline-flex h-16 w-16 items-center justify-center rounded-full bg-navy-800/30 border border-navy-700/50 mb-4">
          <RocketLaunchIcon class="h-8 w-8 text-navy-500" />
        </div>
        <h3 class="text-lg font-medium text-parchment">Ready to find your next opportunity</h3>
        <p class="mt-2 text-sm text-navy-400 max-w-md mx-auto">
          Click the button above to scan the opportunity landscape and find matches that align with your profile.
        </p>
        <div class="mt-4 flex items-center justify-center gap-2 text-xs text-navy-500">
          <CheckCircleIcon class="h-3.5 w-3.5 text-chart-400" />
          <span>Powered by semantic search + AI ranking</span>
        </div>
      </div>
    </main>
  </div>
</template>