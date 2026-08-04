<script setup lang="ts">
import { 
  Icon as IconifyIcon,
  SparklesIcon,
  DocumentTextIcon,
  EnvelopeIcon,
  PhotoIcon,
  AcademicCapIcon,
  LightBulbIcon,
  CalendarIcon,
  ArrowPathIcon,
  XMarkIcon
} from '@heroicons/vue/24/outline';

const route = useRoute();
const api = useApi();
const opportunityId = ref((route.query.opportunity_id as string) || "");
const result = ref<any>(null);
const loading = ref(false);
const error = ref("");

async function prepareMe() {
  loading.value = true;
  error.value = "";
  try {
    result.value = await api.post("/career-coach", {
      opportunity_id: opportunityId.value || null,
    });
  } catch (e: any) {
    error.value = e?.data?.detail || "Couldn't generate prep guidance. Try again.";
  } finally {
    loading.value = false;
  }
}
</script>

<template>
  <div class="min-h-screen bg-navy-950 relative">
    <!-- Neural Network Background -->
    <div class="absolute inset-0 pointer-events-none overflow-hidden opacity-[0.04]">
      <svg class="absolute inset-0 h-full w-full" xmlns="http://www.w3.org/2000/svg">
        <!-- Neural Nodes -->
        <g v-for="i in 40" :key="i">
          <circle 
            :cx="Math.random() * 100 + '%'" 
            :cy="Math.random() * 100 + '%'" 
            r="2" 
            fill="#4FD1C5"
            class="animate-pulse"
            :style="{ animationDelay: (i * 0.08) + 's' }"
          />
        </g>
        <!-- Neural Connections -->
        <g v-for="i in 15" :key="'conn-' + i">
          <line 
            :x1="Math.random() * 100 + '%'" 
            :y1="Math.random() * 100 + '%'" 
            :x2="Math.random() * 100 + '%'" 
            :y2="Math.random() * 100 + '%'" 
            stroke="#4FD1C5" 
            stroke-width="0.5"
            opacity="0.3"
          />
        </g>
      </svg>
    </div>

    <!-- Flow Nodes - Static decorative elements -->
    <div class="absolute inset-0 pointer-events-none overflow-hidden">
      <div class="absolute top-[15%] left-[5%] opacity-[0.03]">
        <div class="flex items-center gap-2">
          <div class="h-3 w-3 rounded-full bg-chart-400"></div>
          <div class="h-px w-16 bg-chart-400/20"></div>
          <div class="h-2 w-2 rounded-full bg-chart-400"></div>
          <div class="h-px w-24 bg-chart-400/20"></div>
          <div class="h-3 w-3 rounded-full bg-chart-400"></div>
        </div>
      </div>
      <div class="absolute bottom-[20%] right-[5%] opacity-[0.03]">
        <div class="flex items-center gap-2">
          <div class="h-2 w-2 rounded-full bg-chart-400"></div>
          <div class="h-px w-20 bg-chart-400/20"></div>
          <div class="h-3 w-3 rounded-full bg-chart-400"></div>
          <div class="h-px w-16 bg-chart-400/20"></div>
          <div class="h-2 w-2 rounded-full bg-chart-400"></div>
        </div>
      </div>
    </div>

    <!-- Radial Gradient Overlay -->
    <div class="absolute inset-0 pointer-events-none bg-[radial-gradient(ellipse_at_center,_transparent_0%,_#0A0E1A_100%)] opacity-60"></div>

    <AppNav />
    <main class="relative z-10 mx-auto max-w-4xl px-4 sm:px-6 py-8 sm:py-12">
      
      <!-- Header -->
      <div class="mb-8 pb-6 border-b border-navy-800/50">
        <div class="flex items-center gap-3 mb-2">
          <span class="inline-flex items-center gap-2 rounded-full bg-signal-400/10 px-3 py-1 text-xs font-mono text-signal-400 border border-signal-400/10">
            <span class="h-1.5 w-1.5 rounded-full bg-signal-400 animate-pulse"></span>
            Phase 5
          </span>
          <span class="text-xs font-mono text-navy-500">·</span>
          <span class="text-xs font-mono text-navy-500">AI Career Coach</span>
        </div>
        <h1 class="text-2xl sm:text-3xl font-display font-medium text-parchment tracking-tight">Prepare Me</h1>
        <p class="mt-1.5 text-sm text-navy-400">
          CV notes, cover-letter draft, and interview tips — targeted at a specific opportunity or general prep based on your profile.
        </p>
      </div>

      <!-- Input Section -->
      <div class="rounded-xl bg-navy-900/40 border border-navy-800/50 p-5 sm:p-6 backdrop-blur-sm transition-all hover:border-navy-700/70">
        <div class="space-y-4">
          <div>
            <label class="block text-xs font-mono text-navy-400 uppercase tracking-wider mb-1.5">
              Opportunity ID 
              <span class="normal-case font-mono text-navy-500 text-[10px]">(optional)</span>
            </label>
            <div class="relative">
              <input 
                v-model="opportunityId" 
                class="w-full rounded-lg bg-navy-950/50 border border-navy-800/50 px-4 py-3 text-parchment placeholder-navy-500 focus:border-signal-400/50 focus:outline-none focus:ring-1 focus:ring-signal-400/20 transition-all" 
                placeholder="Leave blank for general prep" 
              />
              <div class="absolute right-3 top-1/2 -translate-y-1/2 flex items-center gap-1.5">
                <div v-if="opportunityId.length > 0" class="h-1.5 w-1.5 rounded-full bg-signal-400 animate-pulse"></div>
              </div>
            </div>
            <p class="mt-1.5 text-[10px] font-mono text-navy-500">Auto-filled from "Prepare me" links</p>
          </div>
          
          <div class="flex items-center gap-4">
            <button 
              class="inline-flex items-center gap-2 rounded-lg bg-signal-400/10 px-5 py-2.5 text-sm font-medium text-signal-400 border border-signal-400/20 hover:bg-signal-400/20 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
              :disabled="loading" 
              @click="prepareMe"
            >
              <SparklesIcon v-if="!loading" class="h-4 w-4" />
              <ArrowPathIcon v-else class="h-4 w-4 animate-spin" />
              {{ loading ? "Preparing..." : "Prepare Me" }}
            </button>
            <p v-if="error" class="text-sm text-coral-400 flex-1">{{ error }}</p>
          </div>
        </div>
      </div>

      <!-- Results -->
      <section v-if="result" class="mt-10 space-y-6">
        <!-- Loading animation for results -->
        <div class="flex items-center gap-2 text-xs font-mono text-navy-500 mb-4">
          <div class="h-1.5 w-1.5 rounded-full bg-signal-400 animate-pulse"></div>
          <span>Preparation complete</span>
        </div>

        <!-- CV Suggestions -->
        <div class="rounded-xl bg-navy-900/40 border border-navy-800/50 p-5 sm:p-6 backdrop-blur-sm transition-all hover:border-navy-700/70">
          <div class="flex items-center gap-3 mb-4">
            <div class="flex h-8 w-8 items-center justify-center rounded-lg bg-chart-400/10 border border-chart-400/20">
              <DocumentTextIcon class="h-4 w-4 text-chart-400" />
            </div>
            <h2 class="text-base font-medium text-parchment">CV Suggestions</h2>
            <span class="ml-auto rounded-full bg-navy-800/50 px-2 py-0.5 text-xs font-mono text-navy-400">{{ result.cv_suggestions?.length || 0 }}</span>
          </div>
          <ul class="space-y-2">
            <li v-for="(s, index) in result.cv_suggestions" :key="s" class="flex items-start gap-3 text-sm text-navy-300">
              <span class="mt-0.5 text-xs font-mono text-navy-500">{{ String(index + 1).padStart(2, '0') }}</span>
              <span>{{ s }}</span>
            </li>
          </ul>
        </div>

        <!-- Cover Letter -->
        <div class="rounded-xl bg-navy-900/40 border border-navy-800/50 p-5 sm:p-6 backdrop-blur-sm transition-all hover:border-navy-700/70">
          <div class="flex items-center gap-3 mb-4">
            <div class="flex h-8 w-8 items-center justify-center rounded-lg bg-signal-400/10 border border-signal-400/20">
              <EnvelopeIcon class="h-4 w-4 text-signal-400" />
            </div>
            <h2 class="text-base font-medium text-parchment">Cover Letter Draft</h2>
          </div>
          <div class="rounded-lg bg-navy-950/50 border border-navy-800/50 p-4">
            <p class="whitespace-pre-line text-sm text-parchment leading-relaxed">{{ result.cover_letter_draft }}</p>
          </div>
        </div>

        <!-- Two Column Grid -->
        <div class="grid gap-6 sm:grid-cols-2">
          <!-- Portfolio Improvements -->
          <div class="rounded-xl bg-navy-900/40 border border-navy-800/50 p-5 backdrop-blur-sm transition-all hover:border-navy-700/70">
            <div class="flex items-center gap-3 mb-4">
              <div class="flex h-8 w-8 items-center justify-center rounded-lg bg-coral-400/10 border border-coral-400/20">
                <PhotoIcon class="h-4 w-4 text-coral-400" />
              </div>
              <h2 class="text-base font-medium text-parchment">Portfolio</h2>
              <span class="ml-auto rounded-full bg-navy-800/50 px-2 py-0.5 text-xs font-mono text-navy-400">{{ result.portfolio_improvements?.length || 0 }}</span>
            </div>
            <ul class="space-y-2">
              <li v-for="(p, index) in result.portfolio_improvements" :key="p" class="flex items-start gap-3 text-sm text-navy-300">
                <span class="mt-0.5 text-xs font-mono text-navy-500">{{ String(index + 1).padStart(2, '0') }}</span>
                <span>{{ p }}</span>
              </li>
            </ul>
          </div>

          <!-- Skills to Learn -->
          <div class="rounded-xl bg-navy-900/40 border border-navy-800/50 p-5 backdrop-blur-sm transition-all hover:border-navy-700/70">
            <div class="flex items-center gap-3 mb-4">
              <div class="flex h-8 w-8 items-center justify-center rounded-lg bg-parchment-400/10 border border-parchment-400/20">
                <AcademicCapIcon class="h-4 w-4 text-parchment-400" />
              </div>
              <h2 class="text-base font-medium text-parchment">Skills to Learn</h2>
              <span class="ml-auto rounded-full bg-navy-800/50 px-2 py-0.5 text-xs font-mono text-navy-400">{{ result.skills_to_learn?.length || 0 }}</span>
            </div>
            <ul class="space-y-2">
              <li v-for="(s, index) in result.skills_to_learn" :key="s" class="flex items-start gap-3 text-sm text-navy-300">
                <span class="mt-0.5 text-xs font-mono text-navy-500">{{ String(index + 1).padStart(2, '0') }}</span>
                <span>{{ s }}</span>
              </li>
            </ul>
          </div>
        </div>

        <!-- Interview Tips -->
        <div class="rounded-xl bg-navy-900/40 border border-navy-800/50 p-5 sm:p-6 backdrop-blur-sm transition-all hover:border-navy-700/70">
          <div class="flex items-center gap-3 mb-4">
            <div class="flex h-8 w-8 items-center justify-center rounded-lg bg-chart-400/10 border border-chart-400/20">
              <LightBulbIcon class="h-4 w-4 text-chart-400" />
            </div>
            <h2 class="text-base font-medium text-parchment">Interview Tips</h2>
            <span class="ml-auto rounded-full bg-navy-800/50 px-2 py-0.5 text-xs font-mono text-navy-400">{{ result.interview_tips?.length || 0 }}</span>
          </div>
          <ul class="space-y-2">
            <li v-for="(t, index) in result.interview_tips" :key="t" class="flex items-start gap-3 text-sm text-navy-300">
              <span class="mt-0.5 text-xs font-mono text-navy-500">{{ String(index + 1).padStart(2, '0') }}</span>
              <span>{{ t }}</span>
            </li>
          </ul>
        </div>

        <!-- Timeline -->
        <div class="rounded-xl bg-navy-900/40 border border-navy-800/50 p-5 sm:p-6 backdrop-blur-sm transition-all hover:border-navy-700/70">
          <div class="flex items-center gap-3 mb-4">
            <div class="flex h-8 w-8 items-center justify-center rounded-lg bg-signal-400/10 border border-signal-400/20">
              <CalendarIcon class="h-4 w-4 text-signal-400" />
            </div>
            <h2 class="text-base font-medium text-parchment">Timeline</h2>
            <span class="ml-auto rounded-full bg-navy-800/50 px-2 py-0.5 text-xs font-mono text-navy-400">{{ result.timeline?.length || 0 }}</span>
          </div>
          <div class="relative">
            <div class="absolute left-3 top-0 bottom-0 w-px bg-gradient-to-b from-signal-400/30 via-signal-400/10 to-transparent"></div>
            <ul class="space-y-4">
              <li v-for="(t, index) in result.timeline" :key="t" class="relative pl-10">
                <div class="absolute left-0 top-1 flex h-6 w-6 items-center justify-center rounded-full bg-navy-800/50 border border-signal-400/30">
                  <span class="text-[10px] font-mono font-medium text-signal-400">{{ index + 1 }}</span>
                </div>
                <p class="text-sm text-navy-300">{{ t }}</p>
              </li>
            </ul>
          </div>
        </div>
      </section>
    </main>
  </div>
</template>