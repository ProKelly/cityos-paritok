<script setup lang="ts">
import { ref, onMounted } from 'vue';
import {
  ArrowLeftIcon,
  BuildingOfficeIcon,
  MapPinIcon,
  CalendarIcon,
  ClockIcon,
  UserGroupIcon,
  WrenchScrewdriverIcon,
  DocumentTextIcon,
  SparklesIcon,
  BookmarkIcon,
  BookmarkSlashIcon,
  CheckCircleIcon,
  XCircleIcon,
  ArrowPathIcon,
  GlobeAltIcon,
  AcademicCapIcon,
  EnvelopeIcon,
  ShareIcon,
  ArrowTopRightOnSquareIcon
} from '@heroicons/vue/24/outline';

const route = useRoute();
const api = useApi();
const opp = ref<any>(null);
const loading = ref(true);
const error = ref("");
const saved = ref(false);
const applying = ref(false);
const applied = ref(false);

async function load() {
  loading.value = true;
  error.value = "";
  try {
    opp.value = await api.get(`/opportunities/${route.params.id}`);
    // Check if already saved
    try {
      const savedList = await api.get("/opportunities/saved/list");
      saved.value = savedList.some((o: any) => o.id === route.params.id);
    } catch (e) {
      // ignore
    }
  } catch (e: any) {
    error.value = e?.data?.detail || "Couldn't load this opportunity.";
  } finally {
    loading.value = false;
  }
}
onMounted(load);

async function save() {
  if (saved.value) {
    await api.del(`/opportunities/${route.params.id}/save`);
    saved.value = false;
  } else {
    await api.post(`/opportunities/${route.params.id}/save`);
    saved.value = true;
  }
}

async function markApplied() {
  applying.value = true;
  try {
    await api.post("/applications", { opportunity_id: route.params.id, status: "applied" });
    applied.value = true;
  } finally {
    applying.value = false;
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
      
      <!-- Back Link -->
      <NuxtLink to="/opportunities/find" class="group inline-flex items-center gap-2 text-sm text-navy-400 hover:text-parchment transition-colors mb-6">
        <ArrowLeftIcon class="h-4 w-4 group-hover:-translate-x-0.5 transition-transform" />
        Back to matches
      </NuxtLink>

      <!-- Loading State -->
      <div v-if="loading" class="flex flex-col items-center justify-center py-20">
        <ArrowPathIcon class="h-8 w-8 animate-spin text-chart-400" />
        <p class="mt-4 text-sm text-navy-500">Loading opportunity details...</p>
      </div>

      <!-- Error State -->
      <div v-else-if="error" class="rounded-xl bg-coral-400/5 border border-coral-400/20 p-6 flex items-start gap-3">
        <XCircleIcon class="h-5 w-5 text-coral-400 flex-shrink-0 mt-0.5" />
        <div>
          <p class="text-sm text-coral-400">{{ error }}</p>
          <button @click="load" class="mt-2 text-sm text-chart-400 hover:text-chart-300 transition-colors">
            Try again
          </button>
        </div>
      </div>

      <!-- Opportunity Details -->
      <template v-else-if="opp">
        <!-- Header -->
        <div class="mb-8">
          <div class="flex items-center gap-2 flex-wrap mb-3">
            <span class="inline-flex items-center gap-1 rounded-full bg-navy-800/50 px-3 py-1 text-xs font-mono text-navy-400 border border-navy-700/50">
              <BuildingOfficeIcon class="h-3 w-3" />
              {{ opp.category || 'Opportunity' }}
            </span>
            <span v-if="opp.country" class="inline-flex items-center gap-1 rounded-full bg-navy-800/50 px-3 py-1 text-xs font-mono text-navy-400 border border-navy-700/50">
              <MapPinIcon class="h-3 w-3" />
              {{ opp.country }}
            </span>
            <span v-if="opp.remote" class="inline-flex items-center gap-1 rounded-full bg-chart-400/10 px-3 py-1 text-xs font-mono text-chart-400 border border-chart-400/20">
              <GlobeAltIcon class="h-3 w-3" />
              Remote
            </span>
          </div>

          <h1 class="text-2xl sm:text-3xl font-display font-medium text-parchment tracking-tight">{{ opp.title }}</h1>
          <p class="mt-1.5 text-sm text-navy-400 flex items-center gap-2">
            <BuildingOfficeIcon class="h-4 w-4" />
            {{ opp.organization }}
          </p>
        </div>

        <!-- Main Card -->
        <div class="rounded-xl bg-navy-900/40 border border-navy-800/50 p-5 sm:p-6 backdrop-blur-sm transition-all hover:border-navy-700/70">
          
          <!-- Description -->
          <div class="prose prose-invert max-w-none">
            <p class="text-parchment leading-relaxed">{{ opp.description }}</p>
          </div>

          <!-- Details Grid -->
          <dl class="mt-6 grid gap-4 sm:grid-cols-2 border-t border-navy-800/50 pt-6">
            <div>
              <dt class="flex items-center gap-2 text-xs font-mono text-navy-400 uppercase tracking-wider">
                <CalendarIcon class="h-3.5 w-3.5" />
                Deadline
              </dt>
              <dd class="mt-1.5 text-sm text-coral-400 font-medium">
                {{ opp.deadline || "Rolling / not specified" }}
              </dd>
            </div>
            <div>
              <dt class="flex items-center gap-2 text-xs font-mono text-navy-400 uppercase tracking-wider">
                <UserGroupIcon class="h-3.5 w-3.5" />
                Eligibility
              </dt>
              <dd class="mt-1.5 text-sm text-parchment">
                {{ opp.eligibility || "See listing for details" }}
              </dd>
            </div>
            <div v-if="opp.salary">
              <dt class="flex items-center gap-2 text-xs font-mono text-navy-400 uppercase tracking-wider">
                CurrencyDollarIcon
                Salary
              </dt>
              <dd class="mt-1.5 text-sm text-parchment">{{ opp.salary }}</dd>
            </div>
            <div v-if="opp.experience_level">
              <dt class="flex items-center gap-2 text-xs font-mono text-navy-400 uppercase tracking-wider">
                <AcademicCapIcon class="h-3.5 w-3.5" />
                Experience Level
              </dt>
              <dd class="mt-1.5 text-sm text-parchment">{{ opp.experience_level }}</dd>
            </div>
          </dl>

          <!-- Skills -->
          <div v-if="opp.skills?.length" class="mt-6 pt-6 border-t border-navy-800/50">
            <p class="flex items-center gap-2 text-xs font-mono text-navy-400 uppercase tracking-wider mb-3">
              <WrenchScrewdriverIcon class="h-3.5 w-3.5" />
              Required Skills
            </p>
            <div class="flex flex-wrap gap-2">
              <span v-for="s in opp.skills" :key="s" class="rounded-full bg-navy-800/30 border border-navy-700/50 px-3 py-1.5 text-xs text-navy-300">
                {{ s }}
              </span>
            </div>
          </div>

          <!-- Tags -->
          <div v-if="opp.tags?.length" class="mt-4 pt-4 border-t border-navy-800/50">
            <div class="flex flex-wrap gap-1.5">
              <span v-for="tag in opp.tags" :key="tag" class="rounded-full bg-navy-800/20 px-2.5 py-0.5 text-[10px] text-navy-400 border border-navy-700/30">
                #{{ tag }}
              </span>
            </div>
          </div>

          <!-- Actions -->
          <div class="mt-8 pt-6 border-t border-navy-800/50 flex flex-wrap items-center gap-3">
            <a 
              :href="opp.url" 
              target="_blank" 
              rel="noopener" 
              class="inline-flex items-center gap-2 rounded-lg bg-chart-400/10 px-5 py-2.5 text-sm font-medium text-chart-400 border border-chart-400/20 hover:bg-chart-400/20 transition-all"
            >
              <ArrowTopRightOnSquareIcon class="h-4 w-4" />
              Apply Now
            </a>
            
            <button 
              class="inline-flex items-center gap-2 rounded-lg bg-navy-800/30 px-4 py-2.5 text-sm font-medium text-parchment border border-navy-700/50 hover:bg-navy-800/50 hover:border-navy-700/70 transition-all"
              @click="save"
            >
              <BookmarkIcon v-if="!saved" class="h-4 w-4" />
              <BookmarkSlashIcon v-else class="h-4 w-4" />
              {{ saved ? "Saved" : "Save" }}
            </button>

            <NuxtLink 
              :to="`/career-coach?opportunity_id=${opp.id}`" 
              class="inline-flex items-center gap-2 rounded-lg bg-signal-400/10 px-4 py-2.5 text-sm font-medium text-signal-400 border border-signal-400/20 hover:bg-signal-400/20 transition-all"
            >
              <SparklesIcon class="h-4 w-4" />
              Prepare Me
            </NuxtLink>

            <button 
              class="inline-flex items-center gap-2 rounded-lg bg-navy-800/30 px-4 py-2.5 text-sm font-medium text-parchment border border-navy-700/50 hover:bg-navy-800/50 hover:border-navy-700/70 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
              :disabled="applying || applied" 
              @click="markApplied"
            >
              <CheckCircleIcon v-if="applied" class="h-4 w-4 text-chart-400" />
              <ArrowPathIcon v-else-if="applying" class="h-4 w-4 animate-spin" />
              <ClockIcon v-else class="h-4 w-4" />
              {{ applied ? "Applied" : applying ? "Saving..." : "Mark as applied" }}
            </button>

            <button 
              class="inline-flex items-center gap-1.5 rounded-lg bg-navy-800/30 px-3 py-2.5 text-sm font-medium text-navy-400 border border-navy-700/50 hover:bg-navy-800/50 hover:text-parchment transition-all ml-auto"
              @click="navigator.share?.({ title: opp.title, url: window.location.href })"
            >
              <ShareIcon class="h-4 w-4" />
            </button>
          </div>

          <!-- Applied Success Message -->
          <div v-if="applied" class="mt-4 rounded-lg bg-chart-400/5 border border-chart-400/20 p-3 flex items-center gap-2.5">
            <CheckCircleIcon class="h-5 w-5 text-chart-400" />
            <p class="text-sm text-chart-400">Great! You've marked this as applied. Track your applications in the dashboard.</p>
          </div>

          <!-- Saved Success Message -->
          <div v-if="saved" class="mt-4 rounded-lg bg-chart-400/5 border border-chart-400/20 p-3 flex items-center gap-2.5">
            <BookmarkIcon class="h-5 w-5 text-chart-400" />
            <p class="text-sm text-chart-400">This opportunity has been saved to your shortlist.</p>
          </div>
        </div>

        <!-- Related Opportunities -->
        <div v-if="opp.related?.length" class="mt-8">
          <h2 class="text-sm font-medium text-parchment mb-4 flex items-center gap-2">
            <SparklesIcon class="h-4 w-4 text-navy-400" />
            Similar Opportunities
          </h2>
          <div class="grid gap-3 sm:grid-cols-2">
            <NuxtLink 
              v-for="related in opp.related.slice(0, 2)" 
              :key="related.id"
              :to="`/opportunities/${related.id}`"
              class="rounded-lg bg-navy-900/30 border border-navy-800/50 p-4 transition-all hover:border-navy-700/70 hover:bg-navy-900/50"
            >
              <p class="text-sm font-medium text-parchment">{{ related.title }}</p>
              <p class="text-xs text-navy-500 mt-1">{{ related.organization }}</p>
            </NuxtLink>
          </div>
        </div>
      </template>
    </main>
  </div>
</template>