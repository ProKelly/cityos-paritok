<script setup lang="ts">
import { ref, onMounted } from 'vue';
import {
  SparklesIcon,
  UserIcon,
  FingerPrintIcon,
  MagnifyingGlassIcon,
  MapIcon,
  DocumentTextIcon,
  RocketLaunchIcon,
  ArrowRightIcon,
  CheckCircleIcon,
  ChartBarIcon,
  LightBulbIcon,
  UserGroupIcon,
  GlobeAltIcon,
  AcademicCapIcon,
  BriefcaseIcon,
  BookmarkIcon,
  CloudArrowUpIcon,
  ShieldCheckIcon,
  CpuChipIcon,
  BeakerIcon,
  PresentationChartLineIcon
} from '@heroicons/vue/24/outline';

definePageMeta({ layout: false });

const waypoints = [
  { 
    label: "Chart your profile", 
    copy: "Answer a few plain questions — skills, goals, where you want to go. No 40-field forms.",
    icon: UserIcon,
    color: "text-chart-400"
  },
  { 
    label: "Get your Opportunity DNA", 
    copy: "Our AI reads your profile and summarizes your strengths, gaps, and best-fit categories.",
    icon: FingerPrintIcon,
    color: "text-signal-400"
  },
  { 
    label: "See your matches", 
    copy: "Semantic search plus an AI reasoning pass ranks the opportunities that actually fit — with a plain-English reason for each.",
    icon: MagnifyingGlassIcon,
    color: "text-chart-400"
  },
  { 
    label: "Follow your roadmap", 
    copy: "Tell us a goal and get a realistic, month-by-month plan to get there.",
    icon: MapIcon,
    color: "text-signal-400"
  },
  { 
    label: "Apply, prepared", 
    copy: "CV notes, a cover-letter draft, and interview tips generated for the specific opportunity you're chasing.",
    icon: DocumentTextIcon,
    color: "text-chart-400"
  },
];

const stats = [
  { value: "94%", label: "Match accuracy", icon: ChartBarIcon },
  { value: "98%", label: "User satisfaction", icon: PresentationChartLineIcon },
];

const features = [
  { icon: AcademicCapIcon, title: "For students & early-career", description: "Built specifically for those navigating their next move." },
  { icon: CloudArrowUpIcon, title: "AI-powered matching", description: "Semantic search + AI reasoning finds the best fits." },
  { icon: BookmarkIcon, title: "Save & track", description: "Keep your shortlist organized and track your progress." },
];

const about = {
  title: "Built for the next generation of talent",
  description: "CityOS AI was created to bridge the gap between ambition and opportunity. We believe that every talented individual deserves a clear path to their next big break — whether it's a scholarship, job, grant, or competition.",
  details: [
    {
      icon: CpuChipIcon,
      title: "AI-First Approach",
      description: "Our matching engine uses semantic search and AI reasoning to find opportunities that truly fit your profile."
    },
    {
      icon: BeakerIcon,
      title: "Research-Backed",
      description: "Built on the latest research in natural language processing and recommendation systems."
    },
    {
      icon: ShieldCheckIcon,
      title: "Privacy First",
      description: "Your data is yours. We only use it to find better matches, never to sell or share."
    }
  ]
};
</script>

<template>
  <div class="min-h-screen bg-navy-950 relative overflow-hidden">
    <!-- Neural Network Background -->
    <div class="absolute inset-0 pointer-events-none overflow-hidden opacity-[0.03]">
      <svg class="absolute inset-0 h-full w-full" xmlns="http://www.w3.org/2000/svg">
        <g v-for="i in 50" :key="i">
          <circle 
            :cx="Math.random() * 100 + '%'" 
            :cy="Math.random() * 100 + '%'" 
            r="2" 
            fill="#4FD1C5"
            class="animate-pulse"
            :style="{ animationDelay: (i * 0.1) + 's' }"
          />
        </g>
        <g v-for="i in 20" :key="'conn-' + i">
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
        <!-- Neural Flow Path -->
        <path 
          d="M 10% 30% Q 30% 15% 50% 40% T 75% 30% T 90% 50%" 
          stroke="#4FD1C5" 
          stroke-width="1"
          fill="none"
          opacity="0.15"
          stroke-dasharray="4 6"
        />
        <path 
          d="M 15% 70% Q 35% 85% 55% 65% T 80% 75% T 95% 60%" 
          stroke="#4FD1C5" 
          stroke-width="1"
          fill="none"
          opacity="0.12"
          stroke-dasharray="3 8"
        />
      </svg>
    </div>

    <!-- Neural Node Clusters -->
    <div class="absolute inset-0 pointer-events-none overflow-hidden opacity-[0.02]">
      <div class="absolute top-[5%] left-[3%]">
        <div class="flex items-center gap-8">
          <div class="h-3 w-3 rounded-full bg-chart-400"></div>
          <div class="h-px w-24 bg-chart-400/20"></div>
          <div class="h-2 w-2 rounded-full bg-chart-400"></div>
          <div class="h-px w-16 bg-chart-400/20"></div>
          <div class="h-4 w-4 rounded-full bg-chart-400"></div>
        </div>
      </div>
      <div class="absolute bottom-[10%] right-[3%]">
        <div class="flex items-center gap-8">
          <div class="h-2 w-2 rounded-full bg-chart-400"></div>
          <div class="h-px w-20 bg-chart-400/20"></div>
          <div class="h-3 w-3 rounded-full bg-chart-400"></div>
          <div class="h-px w-24 bg-chart-400/20"></div>
          <div class="h-3 w-3 rounded-full bg-chart-400"></div>
        </div>
      </div>
    </div>

    <!-- Decorative Blur Elements -->
    <div class="absolute inset-0 pointer-events-none">
      <div class="absolute top-20 -left-20 h-96 w-96 rounded-full bg-chart-400/5 blur-3xl"></div>
      <div class="absolute bottom-20 -right-20 h-96 w-96 rounded-full bg-signal-400/5 blur-3xl"></div>
    </div>

    <!-- Hero Section -->
    <section class="relative mx-auto flex min-h-[90vh] max-w-7xl flex-col items-center justify-center px-4 sm:px-6 text-center pt-16">
      <!-- Radar Animation Background -->
      <div class="pointer-events-none absolute left-1/2 top-1/2 -z-0 h-[640px] w-[640px] -translate-x-1/2 -translate-y-1/2 opacity-60">
        <svg viewBox="0 0 640 640" class="h-full w-full">
          <circle cx="320" cy="320" r="120" fill="none" stroke="#262E52" stroke-width="1" />
          <circle cx="320" cy="320" r="220" fill="none" stroke="#262E52" stroke-width="1" />
          <circle cx="320" cy="320" r="300" fill="none" stroke="#1B2140" stroke-width="1" />
          <g class="radar-sweep" style="transform-origin: 320px 320px;">
            <path d="M320 320 L320 20 A300 300 0 0 1 578 170 Z" fill="url(#sweepGradient)" />
          </g>
          <defs>
            <linearGradient id="sweepGradient" x1="320" y1="320" x2="578" y2="170" gradientUnits="userSpaceOnUse">
              <stop offset="0%" stop-color="#F2B84B" stop-opacity="0.35" />
              <stop offset="100%" stop-color="#F2B84B" stop-opacity="0" />
            </linearGradient>
          </defs>
          <circle cx="420" cy="220" r="5" fill="#4FD1C5" class="pulse-ring" style="transform-origin: 420px 220px;" />
          <circle cx="420" cy="220" r="4" fill="#4FD1C5" />
          <circle cx="230" cy="420" r="4" fill="#F2B84B" />
          <circle cx="230" cy="420" r="5" fill="#F2B84B" class="pulse-ring" style="transform-origin: 230px 420px; animation-delay: 1s;" />
          <circle cx="470" cy="410" r="4" fill="#4FD1C5" />
        </svg>
      </div>

      <!-- Logo -->
      <div class="relative z-10 mb-8">
        <img src="/cityos.svg" alt="CityOS Logo" class="h-20 w-auto sm:h-24 object-contain" />
      </div>

      <!-- Badge -->
      <div class="relative z-10 mb-6 inline-flex items-center gap-2 rounded-full bg-chart-400/10 px-4 py-1.5 text-xs font-mono text-chart-400 border border-chart-400/10">
        <SparklesIcon class="h-3.5 w-3.5" />
        Your AI-powered opportunity navigator
      </div>

      <!-- Headline -->
      <h1 class="relative z-10 max-w-3xl text-3xl font-display font-medium leading-tight text-parchment sm:text-5xl lg:text-6xl">
        Stop searching for opportunities.
        <span class="text-signal-400">Get charted a course to them.</span>
      </h1>
      
      <p class="relative z-10 mt-6 max-w-xl text-base text-navy-300 sm:text-lg">
        Tell CityOS AI who you are. It finds the scholarships, jobs, grants, and
        competitions that fit — explains why — and builds the plan to get you there.
      </p>

      <!-- CTA Buttons -->
      <div class="relative z-10 mt-10 flex flex-col gap-4 sm:flex-row">
        <NuxtLink to="/signup" class="inline-flex items-center gap-2 rounded-lg bg-chart-400/10 px-6 py-3 text-sm font-medium text-chart-400 border border-chart-400/20 hover:bg-chart-400/20 transition-all">
          <RocketLaunchIcon class="h-4 w-4" />
          Chart my course
          <ArrowRightIcon class="h-4 w-4" />
        </NuxtLink>
        <NuxtLink to="/login" class="inline-flex items-center gap-2 rounded-lg bg-yellow-200/30 px-6 py-3 text-sm font-medium text-parchment border border-yellow-300/50 hover:bg-navy-800/50 hover:border-navy-700/70 transition-all">
          I already have an account
        </NuxtLink>
      </div>

      <!-- Trust Indicators -->
      <div class="relative z-10 mt-12 flex flex-wrap items-center justify-center gap-6 sm:gap-10">
        <div v-for="stat in stats" :key="stat.label" class="flex items-center gap-2">
          <component :is="stat.icon" class="h-4 w-4 text-chart-400" />
          <div>
            <span class="text-sm font-medium text-parchment">{{ stat.value }}</span>
            <span class="text-xs text-navy-400 ml-1">{{ stat.label }}</span>
          </div>
        </div>
      </div>
    </section>

    <!-- Features Section -->
    <section class="relative z-10 mx-auto max-w-6xl px-4 sm:px-6 pb-20">
      <div class="text-center mb-12">
        <h2 class="text-2xl sm:text-3xl font-display font-medium text-parchment">Why CityOS?</h2>
        <p class="mt-2 text-sm text-navy-400">Everything you need to navigate your career journey</p>
      </div>
      <div class="grid gap-6 sm:grid-cols-3">
        <div v-for="feature in features" :key="feature.title" class="rounded-xl bg-navy-900/40 border border-navy-800/50 p-6 backdrop-blur-sm transition-all hover:border-navy-700/70 hover:bg-navy-900/50">
          <div class="flex h-12 w-12 items-center justify-center rounded-lg bg-chart-400/10 border border-chart-400/20 mb-4">
            <component :is="feature.icon" class="h-6 w-6 text-chart-400" />
          </div>
          <h3 class="text-base font-medium text-parchment">{{ feature.title }}</h3>
          <p class="mt-1.5 text-sm text-navy-400">{{ feature.description }}</p>
        </div>
      </div>
    </section>

    <!-- Process Waypoints -->
    <section class="relative z-10 mx-auto max-w-4xl px-4 sm:px-6 pb-24">
      <div class="text-center mb-12">
        <h2 class="text-2xl sm:text-3xl font-display font-medium text-parchment">How the course is charted</h2>
        <p class="mt-2 text-sm text-navy-400">A clear path from start to success</p>
      </div>

      <ol class="relative space-y-4">
        <!-- Vertical Line -->
        <div class="absolute left-5 top-4 bottom-0 w-px bg-gradient-to-b from-chart-400/30 via-chart-400/10 to-transparent hidden sm:block"></div>
        
        <li v-for="(wp, i) in waypoints" :key="wp.label" class="group relative rounded-xl bg-navy-900/40 border border-navy-800/50 p-5 sm:p-6 backdrop-blur-sm transition-all hover:border-navy-700/70 hover:bg-navy-900/50 pl-14 sm:pl-16">
          <!-- Number/Icon -->
          <div class="absolute left-3 sm:left-4 top-4 flex h-8 w-8 items-center justify-center rounded-full bg-navy-800/50 border border-navy-700/50 group-hover:border-chart-400/30 transition-all">
            <component :is="wp.icon" class="h-4 w-4" :class="wp.color" />
          </div>
          
          <div>
            <div class="flex items-center gap-2 mb-0.5">
              <span class="text-xs font-mono text-navy-500">0{{ i + 1 }}</span>
              <h3 class="text-base font-medium text-parchment">{{ wp.label }}</h3>
            </div>
            <p class="text-sm text-navy-400">{{ wp.copy }}</p>
          </div>
        </li>
      </ol>
    </section>

    <!-- About Section with Neural Nodes -->
    <section class="relative z-10 mx-auto max-w-5xl px-4 sm:px-6 pb-24">
      <div class="text-center mb-12">
        <h2 class="text-2xl sm:text-3xl font-display font-medium text-parchment">About CityOS AI</h2>
        <p class="mt-2 text-sm text-navy-400">Built for the next generation of talent</p>
      </div>

      <!-- Neural Node Visualization -->
      <div class="relative mb-12 rounded-xl bg-navy-900/30 border border-navy-800/50 p-6 sm:p-8 overflow-hidden">
        <!-- Neural Network SVG -->
        <div class="absolute inset-0 pointer-events-none opacity-[0.06]">
          <svg class="h-full w-full" xmlns="http://www.w3.org/2000/svg">
            <!-- Neural Nodes -->
            <g v-for="i in 20" :key="'about-node-' + i">
              <circle 
                :cx="Math.random() * 100 + '%'" 
                :cy="Math.random() * 100 + '%'" 
                r="3" 
                fill="#4FD1C5"
                class="animate-pulse"
                :style="{ animationDelay: (i * 0.15) + 's' }"
              />
            </g>
            <!-- Neural Connections -->
            <g v-for="i in 10" :key="'about-conn-' + i">
              <line 
                :x1="Math.random() * 100 + '%'" 
                :y1="Math.random() * 100 + '%'" 
                :x2="Math.random() * 100 + '%'" 
                :y2="Math.random() * 100 + '%'" 
                stroke="#4FD1C5" 
                stroke-width="0.8"
                opacity="0.4"
              />
            </g>
            <!-- Central Node Cluster -->
            <circle cx="50%" cy="50%" r="60" fill="none" stroke="#4FD1C5" stroke-width="0.5" opacity="0.3" />
            <circle cx="50%" cy="50%" r="4" fill="#4FD1C5" class="animate-pulse" />
            <line x1="50%" y1="50%" x2="20%" y2="30%" stroke="#4FD1C5" stroke-width="0.8" opacity="0.3" />
            <line x1="50%" y1="50%" x2="80%" y2="30%" stroke="#4FD1C5" stroke-width="0.8" opacity="0.3" />
            <line x1="50%" y1="50%" x2="20%" y2="70%" stroke="#4FD1C5" stroke-width="0.8" opacity="0.3" />
            <line x1="50%" y1="50%" x2="80%" y2="70%" stroke="#4FD1C5" stroke-width="0.8" opacity="0.3" />
          </svg>
        </div>

        <div class="relative z-10">
          <p class="text-parchment leading-relaxed text-center max-w-2xl mx-auto">
            {{ about.description }}
          </p>
        </div>
      </div>

      <!-- About Details -->
      <div class="grid gap-6 sm:grid-cols-3">
        <div v-for="detail in about.details" :key="detail.title" class="group rounded-xl bg-navy-900/40 border border-navy-800/50 p-6 backdrop-blur-sm transition-all hover:border-navy-700/70 hover:bg-navy-900/50">
          <div class="relative">
            <!-- Mini Neural Node -->
            <div class="absolute -top-2 -right-2 h-2 w-2 rounded-full bg-chart-400/20 group-hover:bg-chart-400/40 transition-colors animate-pulse"></div>
            <div class="flex h-12 w-12 items-center justify-center rounded-lg bg-chart-400/10 border border-chart-400/20 mb-4">
              <component :is="detail.icon" class="h-6 w-6 text-chart-400" />
            </div>
            <h3 class="text-base font-medium text-parchment">{{ detail.title }}</h3>
            <p class="mt-1.5 text-sm text-navy-400">{{ detail.description }}</p>
          </div>
        </div>
      </div>
    </section>

    <!-- Footer -->
    <footer class="relative z-10 border-t border-navy-800/50 py-8 text-center text-sm text-navy-400">
      <div class="flex flex-col items-center gap-2">
        <div class="flex items-center gap-2">
          <span class="text-parchment font-medium">CityOS</span>
          <span class="rounded-full bg-chart-400/10 px-2 py-0.5 text-[8px] font-mono uppercase tracking-widest text-chart-400 border border-chart-400/10">AI</span>
        </div>
        <p>Built for students and early-career professionals navigating what's next.</p>
        <div class="flex items-center gap-4 text-xs">
          <NuxtLink to="/privacy" class="hover:text-parchment transition-colors">Privacy</NuxtLink>
          <NuxtLink to="/terms" class="hover:text-parchment transition-colors">Terms</NuxtLink>
          <NuxtLink to="/contact" class="hover:text-parchment transition-colors">Contact</NuxtLink>
        </div>
      </div>
    </footer>
  </div>
</template>

<style scoped>
.radar-sweep {
  animation: radarSpin 8s linear infinite;
}

@keyframes radarSpin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

.pulse-ring {
  animation: pulseRing 2s ease-in-out infinite;
}

@keyframes pulseRing {
  0% {
    r: 4;
    opacity: 1;
  }
  50% {
    r: 12;
    opacity: 0;
  }
  100% {
    r: 4;
    opacity: 0;
  }
}
</style>