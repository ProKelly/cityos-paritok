<script setup lang="ts">
import { 
  MapPinIcon,
  BookmarkIcon,
  PaperAirplaneIcon,
  ChartBarIcon,
  SparklesIcon,
  CalendarIcon,
  ArrowRightIcon,
  CheckCircleIcon,
  XCircleIcon,
  DocumentArrowDownIcon,
  EnvelopeIcon,
  ArrowPathIcon
} from '@heroicons/vue/24/outline';

const api = useApi();
const summary = ref<any>(null);
const loading = ref(true);
const errorMsg = ref("");

async function load() {
  loading.value = true;
  try {
    summary.value = await api.get("/dashboard/summary");
  } catch (e: any) {
    errorMsg.value = e?.data?.detail || "Couldn't load your dashboard.";
  } finally {
    loading.value = false;
  }
}
onMounted(load);

// ── CV & Cover Letter generation ──────────────────────────────────────────
const cvDescription = ref("");
const cvLoading = ref(false);
const cvError = ref("");

const coverDescription = ref("");
const coverLoading = ref(false);
const coverError = ref("");

function slug(name: string) {
  return (name || "document").toLowerCase().trim().replace(/\s+/g, "-").replace(/[^a-z0-9-]/g, "");
}

async function generateAndDownloadCV() {
  cvError.value = "";
  cvLoading.value = true;
  try {
    const cv: any = await api.post("/documents/cv", { description: cvDescription.value });
    await buildCVPdf(cv);
  } catch (e: any) {
    cvError.value = e?.data?.detail || "Couldn't generate your CV. Try again.";
  } finally {
    cvLoading.value = false;
  }
}

async function generateAndDownloadCoverLetter() {
  coverError.value = "";
  coverLoading.value = true;
  try {
    const letter: any = await api.post("/documents/cover-letter", { description: coverDescription.value });
    await buildCoverLetterPdf(letter);
  } catch (e: any) {
    coverError.value = e?.data?.detail || "Couldn't generate your cover letter. Try again.";
  } finally {
    coverLoading.value = false;
  }
}

async function buildCVPdf(cv: any) {
  const { jsPDF } = await import("jspdf");
  const doc = new jsPDF({ unit: "pt", format: "a4" });
  const pageWidth = doc.internal.pageSize.getWidth();
  const pageHeight = doc.internal.pageSize.getHeight();
  const margin = 48;
  const contentWidth = pageWidth - margin * 2;
  let y = margin;

  const ink: [number, number, number] = [26, 26, 46];
  const teal: [number, number, number] = [47, 154, 144];
  const muted: [number, number, number] = [102, 102, 102];
  const line: [number, number, number] = [210, 210, 210];

  function ensureSpace(h: number) {
    if (y + h > pageHeight - margin) {
      doc.addPage();
      y = margin;
    }
  }

  doc.setFont("helvetica", "bold");
  doc.setFontSize(24);
  doc.setTextColor(...ink);
  doc.text(cv.full_name || "", margin, y);
  y += 26;

  doc.setFont("helvetica", "normal");
  doc.setFontSize(12);
  doc.setTextColor(...teal);
  const headlineLines = doc.splitTextToSize(cv.headline || "", contentWidth);
  doc.text(headlineLines, margin, y);
  y += headlineLines.length * 15 + 4;

  if (cv.location) {
    doc.setFontSize(10);
    doc.setTextColor(...muted);
    doc.text(cv.location, margin, y);
    y += 16;
  }

  doc.setDrawColor(...line);
  doc.setLineWidth(0.75);
  doc.line(margin, y, pageWidth - margin, y);
  y += 20;

  function sectionTitle(title: string) {
    ensureSpace(24);
    doc.setFont("helvetica", "bold");
    doc.setFontSize(11);
    doc.setTextColor(...teal);
    doc.text(title.toUpperCase(), margin, y);
    y += 6;
    doc.setDrawColor(...teal);
    doc.setLineWidth(1);
    doc.line(margin, y, margin + 32, y);
    y += 16;
  }

  function paragraph(text: string) {
    doc.setFont("helvetica", "normal");
    doc.setFontSize(10.5);
    doc.setTextColor(60, 60, 60);
    const lines = doc.splitTextToSize(text, contentWidth);
    ensureSpace(lines.length * 13 + 6);
    doc.text(lines, margin, y);
    y += lines.length * 13 + 10;
  }

  function block(items: { heading: string; subheading?: string; bullets?: string[] }[]) {
    for (const item of items) {
      ensureSpace(30);
      doc.setFont("helvetica", "bold");
      doc.setFontSize(11);
      doc.setTextColor(...ink);
      const headingLines = doc.splitTextToSize(item.heading, contentWidth);
      doc.text(headingLines, margin, y);
      y += headingLines.length * 14;

      if (item.subheading) {
        doc.setFont("helvetica", "italic");
        doc.setFontSize(9.5);
        doc.setTextColor(...muted);
        const subLines = doc.splitTextToSize(item.subheading, contentWidth);
        ensureSpace(subLines.length * 12 + 4);
        doc.text(subLines, margin, y);
        y += subLines.length * 12 + 4;
      }

      for (const b of item.bullets || []) {
        doc.setFont("helvetica", "normal");
        doc.setFontSize(10);
        doc.setTextColor(70, 70, 70);
        const bLines = doc.splitTextToSize(`•  ${b}`, contentWidth - 10);
        ensureSpace(bLines.length * 12.5 + 2);
        doc.text(bLines, margin + 8, y);
        y += bLines.length * 12.5 + 2;
      }
      y += 10;
    }
  }

  if (cv.summary) {
    sectionTitle("Summary");
    paragraph(cv.summary);
  }
  if (cv.skills?.length) {
    sectionTitle("Skills");
    paragraph(cv.skills.join("   ·   "));
  }
  if (cv.experience?.length) {
    sectionTitle("Experience & Projects");
    block(cv.experience);
  }
  if (cv.education?.length) {
    sectionTitle("Education");
    block(cv.education);
  }
  if (cv.languages?.length) {
    sectionTitle("Languages");
    paragraph(cv.languages.join("   ·   "));
  }

  const pageCount = doc.getNumberOfPages();
  for (let i = 1; i <= pageCount; i++) {
    doc.setPage(i);
    doc.setFont("helvetica", "normal");
    doc.setFontSize(8);
    doc.setTextColor(160, 160, 160);
    doc.text("Generated by OpportunityOS AI", pageWidth / 2, pageHeight - 24, { align: "center" });
  }

  doc.save(`cv-${slug(cv.full_name)}.pdf`);
}

async function buildCoverLetterPdf(letter: any) {
  const { jsPDF } = await import("jspdf");
  const doc = new jsPDF({ unit: "pt", format: "a4" });
  const pageWidth = doc.internal.pageSize.getWidth();
  const pageHeight = doc.internal.pageSize.getHeight();
  const margin = 56;
  const contentWidth = pageWidth - margin * 2;
  let y = margin;

  const ink: [number, number, number] = [26, 26, 46];
  const muted: [number, number, number] = [110, 110, 110];

  function ensureSpace(h: number) {
    if (y + h > pageHeight - margin) {
      doc.addPage();
      y = margin;
    }
  }

  doc.setFont("helvetica", "bold");
  doc.setFontSize(14);
  doc.setTextColor(...ink);
  doc.text(letter.full_name || "", margin, y);
  y += 20;

  doc.setFont("helvetica", "normal");
  doc.setFontSize(10);
  doc.setTextColor(...muted);
  doc.text(new Date().toLocaleDateString(undefined, { year: "numeric", month: "long", day: "numeric" }), margin, y);
  y += 36;

  doc.setFont("helvetica", "normal");
  doc.setFontSize(11);
  doc.setTextColor(40, 40, 40);
  doc.text(letter.salutation || "Dear Hiring Manager,", margin, y);
  y += 24;

  for (const para of letter.body_paragraphs || []) {
    const lines = doc.splitTextToSize(para, contentWidth);
    ensureSpace(lines.length * 15 + 14);
    doc.text(lines, margin, y);
    y += lines.length * 15 + 14;
  }

  ensureSpace(50);
  doc.text(letter.closing || "Sincerely,", margin, y);
  y += 30;
  doc.setFont("helvetica", "bold");
  doc.text(letter.full_name || "", margin, y);

  const pageCount = doc.getNumberOfPages();
  for (let i = 1; i <= pageCount; i++) {
    doc.setPage(i);
    doc.setFont("helvetica", "normal");
    doc.setFontSize(8);
    doc.setTextColor(160, 160, 160);
    doc.text("Generated by OpportunityOS AI", pageWidth / 2, pageHeight - 24, { align: "center" });
  }

  doc.save(`cover-letter-${slug(letter.full_name)}.pdf`);
}

const cards = computed(() => {
  const s = summary.value;
  if (!s) return [];
  return [
    { label: "Opportunities found", value: s.opportunities_found, icon: MapPinIcon, color: "text-chart-400" },
    { label: "Saved", value: s.saved_count, icon: BookmarkIcon, color: "text-signal-400" },
    { label: "Applied", value: s.applied_count, icon: PaperAirplaneIcon, color: "text-coral-400" },
    { label: "Profile strength", value: `${s.profile_strength}%`, icon: ChartBarIcon, color: "text-parchment-400" },
  ];
});
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

    <!-- Diagonal Accent Lines -->
    <div class="absolute inset-0 pointer-events-none overflow-hidden opacity-[0.02]">
      <div class="absolute -top-1/2 -right-1/4 h-[200%] w-[2px] bg-gradient-to-b from-transparent via-chart-400 to-transparent rotate-12"></div>
      <div class="absolute -top-1/2 -right-1/6 h-[200%] w-[1px] bg-gradient-to-b from-transparent via-chart-400 to-transparent rotate-12 translate-x-8"></div>
    </div>

    <AppNav />
    <main class="relative z-10 mx-auto max-w-6xl px-4 sm:px-6 py-8 sm:py-12">
      
      <!-- Header -->
      <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-8 pb-5 border-b border-navy-800/60">
        <div class="flex items-center gap-3">
          <div>
            <p class="text-xs font-mono text-navy-500 uppercase tracking-wider">Mission control</p>
            <h1 class="text-2xl sm:text-3xl font-display font-medium text-parchment tracking-tight">Dashboard</h1>
          </div>
        </div>
        <div class="flex items-center gap-3">
          <div v-if="summary?.opportunity_dna" class="hidden sm:flex items-center gap-2">
            <span class="inline-flex items-center gap-2 rounded-full bg-navy-800/40 border border-navy-700/50 px-3 py-1 text-xs font-mono text-chart-400 backdrop-blur-sm">
              <span class="h-1.5 w-1.5 rounded-full bg-chart-400 animate-pulse"></span>
              DNA Active
            </span>
          </div>
          <NuxtLink
            to="/opportunities/find"
            class="inline-flex items-center gap-2 rounded-lg bg-chart-400/10 px-5 py-2.5 text-sm font-medium text-chart-400 border border-chart-400/20 hover:bg-chart-400/20 transition-colors shrink-0"
          >
            <SparklesIcon class="h-4 w-4" />
            <span>Start</span>
            <ArrowRightIcon class="h-4 w-4" />
          </NuxtLink>
        </div>
      </div>

      <!-- Loading State -->
      <div v-if="loading" class="flex flex-col items-center justify-center py-20">
        <div class="h-8 w-8 animate-spin rounded-full border-2 border-chart-400 border-t-transparent"></div>
        <p class="mt-4 text-sm text-navy-500">Loading your dashboard...</p>
      </div>

      <template v-else-if="summary">
        <!-- Profile Banner -->
        <div v-if="!summary.opportunity_dna" class="mb-8 rounded-xl bg-navy-900/40 border border-navy-800/50 p-5 sm:p-6 backdrop-blur-sm">
          <div class="sm:flex sm:items-center sm:justify-between gap-4">
            <div>
              <p class="text-sm font-medium text-parchment flex items-center gap-2">
                <SparklesIcon class="h-4 w-4 text-chart-400" />
                Complete your profile
              </p>
              <p class="mt-1 text-sm text-navy-500">Build your Opportunity DNA to get personalized recommendations.</p>
            </div>
            <NuxtLink to="/profile" class="mt-4 sm:mt-0 inline-flex items-center gap-2 rounded-lg bg-chart-400/10 px-5 py-2.5 text-sm font-medium text-chart-400 border border-chart-400/20 hover:bg-chart-400/20 transition-colors shrink-0">
              <span>Build profile</span>
              <ArrowRightIcon class="h-4 w-4" />
            </NuxtLink>
          </div>
        </div>

        <!-- Metrics -->
        <div class="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          <div v-for="c in cards" :key="c.label" class="group rounded-xl bg-navy-900/40 border border-navy-800/50 p-5 transition-all hover:border-navy-700/70 hover:bg-navy-900/60 backdrop-blur-sm">
            <div class="flex items-center justify-between">
              <p class="text-xs font-mono text-navy-500 uppercase tracking-wider">{{ c.label }}</p>
              <component :is="c.icon" class="h-4 w-4 opacity-40 group-hover:opacity-100 transition-opacity" :class="c.color" />
            </div>
            <p class="mt-2 text-2xl sm:text-3xl font-display font-medium text-parchment">{{ c.value }}</p>
            <div class="mt-3 h-[2px] w-0 group-hover:w-full bg-gradient-to-r from-chart-400/0 via-chart-400/30 to-chart-400/0 transition-all duration-500"></div>
          </div>
        </div>

        <!-- Main Content -->
        <div class="mt-8 grid gap-6 lg:grid-cols-2">
          
          <!-- Recommendations -->
          <section class="rounded-xl bg-navy-900/40 border border-navy-800/50 p-5 sm:p-6 backdrop-blur-sm transition-all hover:border-navy-700/70">
            <div class="mb-5 flex items-center justify-between border-b border-navy-800/50 pb-4">
              <h2 class="text-sm font-medium text-parchment flex items-center gap-2">
                <SparklesIcon class="h-4 w-4 text-chart-400" />
                Recommendations
                <span class="rounded-full bg-navy-800/60 px-2 py-0.5 text-xs font-mono text-chart-400">{{ summary.recommendations?.length || 0 }}</span>
              </h2>
              <NuxtLink to="/opportunities/find" class="text-xs text-chart-400 hover:text-chart-300 transition-colors inline-flex items-center gap-1">
                View all
                <ArrowRightIcon class="h-3 w-3" />
              </NuxtLink>
            </div>
            
            <div v-if="!summary.recommendations?.length" class="py-8 text-center text-sm text-navy-500">
              No matches yet. <NuxtLink to="/opportunities/find" class="text-chart-400 hover:underline">Find opportunities</NuxtLink>
            </div>
            
            <ul v-else class="space-y-3">
              <li v-for="m in summary.recommendations" :key="m.opportunity_id" class="group rounded-lg bg-navy-950/50 border border-navy-800/50 p-4 transition-all hover:border-navy-700/70 hover:bg-navy-950/70">
                <div class="flex items-start justify-between gap-3">
                  <div class="min-w-0">
                    <NuxtLink :to="`/opportunities/${m.opportunity_id}`" class="font-medium text-parchment hover:text-chart-400 transition-colors truncate block">
                      {{ m.opportunity?.title }}
                    </NuxtLink>
                    <p class="text-xs text-navy-500 mt-0.5">{{ m.opportunity?.organization }}</p>
                  </div>
                  <div class="shrink-0 rounded-md bg-navy-800/50 px-2.5 py-1 flex items-center gap-1.5">
                    <span class="font-mono text-xs font-medium text-chart-400">{{ m.match_score }}%</span>
                    <CheckCircleIcon class="h-3 w-3 text-chart-400/60" />
                  </div>
                </div>
              </li>
            </ul>
          </section>

          <!-- Deadlines -->
          <section class="rounded-xl bg-navy-900/40 border border-navy-800/50 p-5 sm:p-6 backdrop-blur-sm transition-all hover:border-navy-700/70">
            <div class="mb-5 flex items-center justify-between border-b border-navy-800/50 pb-4">
              <h2 class="text-sm font-medium text-parchment flex items-center gap-2">
                <CalendarIcon class="h-4 w-4 text-coral-400" />
                Upcoming deadlines
                <span class="rounded-full bg-navy-800/60 px-2 py-0.5 text-xs font-mono text-coral-400">{{ summary.upcoming_deadlines?.length || 0 }}</span>
              </h2>
            </div>

            <div v-if="!summary.upcoming_deadlines?.length" class="py-8 text-center text-sm text-navy-500">
              No deadlines tracked yet.
            </div>

            <ul v-else class="space-y-3">
              <li v-for="d in summary.upcoming_deadlines" :key="d.opportunity_id" class="group flex items-center justify-between rounded-lg bg-navy-950/50 border border-navy-800/50 p-4 transition-all hover:border-navy-700/70 hover:bg-navy-950/70">
                <span class="text-parchment font-medium truncate pr-4 text-sm">{{ d.opportunity?.title }}</span>
                <span class="shrink-0 font-mono text-xs rounded-md bg-navy-800/50 px-2.5 py-1 text-coral-400 flex items-center gap-1.5">
                  <CalendarIcon class="h-3 w-3" />
                  {{ d.opportunity?.deadline }}
                </span>
              </li>
            </ul>
          </section>

        </div>

        <!-- Documents -->
        <div v-if="summary.opportunity_dna" class="mt-8 grid gap-6 lg:grid-cols-2">
          <!-- Get my CV -->
          <section class="rounded-xl bg-navy-900/40 border border-navy-800/50 p-5 sm:p-6 backdrop-blur-sm transition-all hover:border-navy-700/70">
            <div class="mb-5 flex items-center gap-3 border-b border-navy-800/50 pb-4">
              <div class="flex h-10 w-10 items-center justify-center rounded-lg bg-chart-400/10 border border-chart-400/20">
                <DocumentArrowDownIcon class="h-5 w-5 text-chart-400" />
              </div>
              <div>
                <p class="text-xs font-mono text-chart-400 uppercase tracking-wider">Document generator</p>
                <p class="text-sm text-parchment font-medium">Get my CV</p>
              </div>
            </div>

            <label class="text-xs font-mono text-navy-500 uppercase tracking-wider mb-1.5 block">
              What should this CV portray about you?
            </label>
            <textarea
              v-model="cvDescription"
              rows="3"
              class="w-full rounded-lg bg-navy-950/50 border border-navy-800/50 px-4 py-3 text-sm text-parchment placeholder-navy-500 focus:border-chart-400/50 focus:outline-none focus:ring-1 focus:ring-chart-400/20 transition-all resize-y"
              placeholder="e.g. Emphasize my backend engineering skills for fintech roles"
            />
            <p class="mt-1.5 text-xs text-navy-500">Built only from your saved profile — nothing is invented.</p>

            <p v-if="cvError" class="mt-3 text-sm text-coral-400 flex items-center gap-2">
              <XCircleIcon class="h-4 w-4 flex-shrink-0" />
              {{ cvError }}
            </p>

            <button
              type="button"
              class="mt-4 inline-flex items-center gap-2 rounded-lg bg-chart-400/10 px-5 py-2.5 text-sm font-medium text-chart-400 border border-chart-400/20 hover:bg-chart-400/20 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
              :disabled="cvLoading"
              @click="generateAndDownloadCV"
            >
              <ArrowPathIcon v-if="cvLoading" class="h-4 w-4 animate-spin" />
              <DocumentArrowDownIcon v-else class="h-4 w-4" />
              {{ cvLoading ? "Building your CV..." : "Get my CV (PDF)" }}
            </button>
          </section>

          <!-- Get me a Cover Letter -->
          <section class="rounded-xl bg-navy-900/40 border border-navy-800/50 p-5 sm:p-6 backdrop-blur-sm transition-all hover:border-navy-700/70">
            <div class="mb-5 flex items-center gap-3 border-b border-navy-800/50 pb-4">
              <div class="flex h-10 w-10 items-center justify-center rounded-lg bg-signal-400/10 border border-signal-400/20">
                <EnvelopeIcon class="h-5 w-5 text-signal-400" />
              </div>
              <div>
                <p class="text-xs font-mono text-signal-400 uppercase tracking-wider">Document generator</p>
                <p class="text-sm text-parchment font-medium">Get me a cover letter</p>
              </div>
            </div>

            <label class="text-xs font-mono text-navy-500 uppercase tracking-wider mb-1.5 block">
              What should this cover letter portray about you?
            </label>
            <textarea
              v-model="coverDescription"
              rows="3"
              class="w-full rounded-lg bg-navy-950/50 border border-navy-800/50 px-4 py-3 text-sm text-parchment placeholder-navy-500 focus:border-signal-400/50 focus:outline-none focus:ring-1 focus:ring-signal-400/20 transition-all resize-y"
              placeholder="e.g. Show enthusiasm plus hands-on project experience"
            />
            <p class="mt-1.5 text-xs text-navy-500">General-purpose by default; generate from an opportunity's page to target it specifically.</p>

            <p v-if="coverError" class="mt-3 text-sm text-coral-400 flex items-center gap-2">
              <XCircleIcon class="h-4 w-4 flex-shrink-0" />
              {{ coverError }}
            </p>

            <button
              type="button"
              class="mt-4 inline-flex items-center gap-2 rounded-lg bg-signal-400/10 px-5 py-2.5 text-sm font-medium text-signal-400 border border-signal-400/20 hover:bg-signal-400/20 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
              :disabled="coverLoading"
              @click="generateAndDownloadCoverLetter"
            >
              <ArrowPathIcon v-if="coverLoading" class="h-4 w-4 animate-spin" />
              <EnvelopeIcon v-else class="h-4 w-4" />
              {{ coverLoading ? "Writing your letter..." : "Get my cover letter (PDF)" }}
            </button>
          </section>
        </div>
      </template>

      <!-- Error -->
      <div v-if="errorMsg" class="mt-6 rounded-lg bg-coral-400/5 border border-coral-400/20 p-4 text-sm text-coral-400 backdrop-blur-sm flex items-start gap-3">
        <XCircleIcon class="h-5 w-5 flex-shrink-0 mt-0.5" />
        <span>{{ errorMsg }}</span>
      </div>
    </main>
  </div>
</template>