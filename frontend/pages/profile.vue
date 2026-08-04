<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue';
import {
  UserIcon,
  GlobeAltIcon,
  AcademicCapIcon,
  WrenchScrewdriverIcon,
  HeartIcon,
  RocketLaunchIcon,
  BuildingOfficeIcon,
  MapPinIcon,
  ClockIcon,
  CurrencyDollarIcon,
  LanguageIcon,
  DocumentTextIcon,
  DocumentArrowDownIcon,
  EnvelopeIcon,
  SparklesIcon,
  CheckCircleIcon,
  XCircleIcon,
  ArrowPathIcon,
  EyeIcon,
  ArrowRightIcon,
  ShieldCheckIcon
} from '@heroicons/vue/24/outline';

const api = useApi();

const form = reactive({
  full_name: "",
  country: "",
  education_level: "",
  skills: "",
  interests: "",
  goals: "",
  preferred_industries: "",
  preferred_countries: "",
  availability: "",
  expected_salary: "",
  languages: "",
  resume_text: "",
});

const dna = ref<any>(null);
const loading = ref(false);
const saving = ref(false);
const error = ref("");
const loaded = ref(false);

function toList(v: string) {
  return v.split(",").map((s) => s.trim()).filter(Boolean);
}
function toCsv(v: string[] | undefined) {
  return (v || []).join(", ");
}

async function loadProfile() {
  loading.value = true;
  try {
    const existing: any = await api.get("/profile");
    if (existing) {
      form.full_name = existing.full_name || "";
      form.country = existing.country || "";
      form.education_level = existing.education_level || "";
      form.skills = toCsv(existing.skills);
      form.interests = toCsv(existing.interests);
      form.goals = existing.goals || "";
      form.preferred_industries = toCsv(existing.preferred_industries);
      form.preferred_countries = toCsv(existing.preferred_countries);
      form.availability = existing.availability || "";
      form.expected_salary = existing.expected_salary || "";
      form.languages = toCsv(existing.languages);
      form.resume_text = existing.resume_text || "";
      dna.value = existing.opportunity_dna;
    }
  } catch (e) {
    // no profile yet — that's fine, this is the creation form
  } finally {
    loading.value = false;
    loaded.value = true;
  }
}

async function onSubmit() {
  error.value = "";
  saving.value = true;
  try {
    const payload = {
      full_name: form.full_name,
      country: form.country,
      education_level: form.education_level,
      skills: toList(form.skills),
      interests: toList(form.interests),
      goals: form.goals,
      preferred_industries: toList(form.preferred_industries),
      preferred_countries: toList(form.preferred_countries),
      availability: form.availability,
      expected_salary: form.expected_salary || null,
      languages: toList(form.languages),
      resume_text: form.resume_text || null,
    };
    const result: any = await api.post("/profile", payload);
    dna.value = result.opportunity_dna;
  } catch (e: any) {
    error.value = e?.data?.detail || "Couldn't save your profile. Try again.";
  } finally {
    saving.value = false;
  }
}

onMounted(loadProfile);

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

  // Header
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

    <div class="absolute inset-0 pointer-events-none bg-[radial-gradient(ellipse_at_center,_transparent_0%,_#0A0E1A_100%)] opacity-60"></div>

    <AppNav />
    <main class="relative z-10 mx-auto max-w-4xl px-4 sm:px-6 py-8 sm:py-12">
      
      <!-- Header -->
      <div class="mb-8 pb-6 border-b border-navy-800/50">
        <div class="flex items-center gap-3 mb-2">
          <span class="inline-flex items-center gap-2 rounded-full bg-chart-400/10 px-3 py-1 text-xs font-mono text-chart-400 border border-chart-400/10">
            <SparklesIcon class="h-3 w-3" />
            Phase 1
          </span>
          <span class="text-xs font-mono text-navy-500">·</span>
          <span class="text-xs font-mono text-navy-500">Chart Yourself</span>
        </div>
        <h1 class="text-2xl sm:text-3xl font-display font-medium text-parchment tracking-tight flex items-center gap-3">
          <UserIcon class="h-6 w-6 text-chart-400" />
          Your Profile
        </h1>
        <p class="mt-1.5 text-sm text-navy-400">
          Plain questions. This feeds your Opportunity DNA — the summary the AI uses to find and explain your matches.
        </p>
      </div>

      <!-- Loading State -->
      <div v-if="loading" class="flex flex-col items-center justify-center py-20">
        <div class="h-8 w-8 animate-spin rounded-full border-2 border-chart-400 border-t-transparent"></div>
        <p class="mt-4 text-sm text-navy-500">Loading your profile...</p>
      </div>

      <!-- Profile Form -->
      <form v-else-if="loaded" class="rounded-xl bg-navy-900/40 border border-navy-800/50 p-5 sm:p-6 backdrop-blur-sm transition-all hover:border-navy-700/70 space-y-6" @submit.prevent="onSubmit">
        <!-- Full Name & Country -->
        <div class="grid gap-4 sm:grid-cols-2">
          <div>
            <label class="flex items-center gap-2 text-xs font-mono text-navy-400 uppercase tracking-wider mb-1.5">
              <UserIcon class="h-3.5 w-3.5" />
              Full name
            </label>
            <input v-model="form.full_name" required class="w-full rounded-lg bg-navy-950/50 border border-navy-800/50 px-4 py-3 text-parchment placeholder-navy-500 focus:border-chart-400/50 focus:outline-none focus:ring-1 focus:ring-chart-400/20 transition-all" placeholder="Your full name" />
          </div>
          <div>
            <label class="flex items-center gap-2 text-xs font-mono text-navy-400 uppercase tracking-wider mb-1.5">
              <GlobeAltIcon class="h-3.5 w-3.5" />
              Country
            </label>
            <input v-model="form.country" required class="w-full rounded-lg bg-navy-950/50 border border-navy-800/50 px-4 py-3 text-parchment placeholder-navy-500 focus:border-chart-400/50 focus:outline-none focus:ring-1 focus:ring-chart-400/20 transition-all" placeholder="e.g. Cameroon" />
          </div>
        </div>

        <!-- Education Level -->
        <div>
          <label class="flex items-center gap-2 text-xs font-mono text-navy-400 uppercase tracking-wider mb-1.5">
            <AcademicCapIcon class="h-3.5 w-3.5" />
            Current education level
          </label>
          <input v-model="form.education_level" required class="w-full rounded-lg bg-navy-950/50 border border-navy-800/50 px-4 py-3 text-parchment placeholder-navy-500 focus:border-chart-400/50 focus:outline-none focus:ring-1 focus:ring-chart-400/20 transition-all" placeholder="e.g. Year 4 Computer Engineering student" />
        </div>

        <!-- Skills -->
        <div>
          <label class="flex items-center gap-2 text-xs font-mono text-navy-400 uppercase tracking-wider mb-1.5">
            <WrenchScrewdriverIcon class="h-3.5 w-3.5" />
            Skills <span class="normal-case font-mono text-navy-500 text-[10px]">(comma-separated)</span>
          </label>
          <input v-model="form.skills" class="w-full rounded-lg bg-navy-950/50 border border-navy-800/50 px-4 py-3 text-parchment placeholder-navy-500 focus:border-chart-400/50 focus:outline-none focus:ring-1 focus:ring-chart-400/20 transition-all" placeholder="Django, Vue.js, PostgreSQL, Flutter" />
        </div>

        <!-- Interests -->
        <div>
          <label class="flex items-center gap-2 text-xs font-mono text-navy-400 uppercase tracking-wider mb-1.5">
            <HeartIcon class="h-3.5 w-3.5" />
            Interests <span class="normal-case font-mono text-navy-500 text-[10px]">(comma-separated)</span>
          </label>
          <input v-model="form.interests" class="w-full rounded-lg bg-navy-950/50 border border-navy-800/50 px-4 py-3 text-parchment placeholder-navy-500 focus:border-chart-400/50 focus:outline-none focus:ring-1 focus:ring-chart-400/20 transition-all" placeholder="AI, fintech, civic tech" />
        </div>

        <!-- Goals -->
        <div>
          <label class="flex items-center gap-2 text-xs font-mono text-navy-400 uppercase tracking-wider mb-1.5">
            <RocketLaunchIcon class="h-3.5 w-3.5" />
            Goals
          </label>
          <textarea v-model="form.goals" rows="3" class="w-full rounded-lg bg-navy-950/50 border border-navy-800/50 px-4 py-3 text-parchment placeholder-navy-500 focus:border-chart-400/50 focus:outline-none focus:ring-1 focus:ring-chart-400/20 transition-all resize-y" placeholder="What are you trying to do in the next 6-12 months?" />
        </div>

        <!-- Preferred Industries & Countries -->
        <div class="grid gap-4 sm:grid-cols-2">
          <div>
            <label class="flex items-center gap-2 text-xs font-mono text-navy-400 uppercase tracking-wider mb-1.5">
              <BuildingOfficeIcon class="h-3.5 w-3.5" />
              Preferred industries <span class="normal-case font-mono text-navy-500 text-[10px]">(comma-sep)</span>
            </label>
            <input v-model="form.preferred_industries" class="w-full rounded-lg bg-navy-950/50 border border-navy-800/50 px-4 py-3 text-parchment placeholder-navy-500 focus:border-chart-400/50 focus:outline-none focus:ring-1 focus:ring-chart-400/20 transition-all" placeholder="Tech, Finance, Healthcare" />
          </div>
          <div>
            <label class="flex items-center gap-2 text-xs font-mono text-navy-400 uppercase tracking-wider mb-1.5">
              <MapPinIcon class="h-3.5 w-3.5" />
              Preferred countries <span class="normal-case font-mono text-navy-500 text-[10px]">(comma-sep)</span>
            </label>
            <input v-model="form.preferred_countries" class="w-full rounded-lg bg-navy-950/50 border border-navy-800/50 px-4 py-3 text-parchment placeholder-navy-500 focus:border-chart-400/50 focus:outline-none focus:ring-1 focus:ring-chart-400/20 transition-all" placeholder="USA, Canada, UK" />
          </div>
        </div>

        <!-- Availability, Salary, Languages -->
        <div class="grid gap-4 sm:grid-cols-3">
          <div>
            <label class="flex items-center gap-2 text-xs font-mono text-navy-400 uppercase tracking-wider mb-1.5">
              <ClockIcon class="h-3.5 w-3.5" />
              Availability
            </label>
            <input v-model="form.availability" class="w-full rounded-lg bg-navy-950/50 border border-navy-800/50 px-4 py-3 text-parchment placeholder-navy-500 focus:border-chart-400/50 focus:outline-none focus:ring-1 focus:ring-chart-400/20 transition-all" placeholder="e.g. Immediately" />
          </div>
          <div>
            <label class="flex items-center gap-2 text-xs font-mono text-navy-400 uppercase tracking-wider mb-1.5">
              <CurrencyDollarIcon class="h-3.5 w-3.5" />
              Expected salary <span class="normal-case font-mono text-navy-500 text-[10px]">(optional)</span>
            </label>
            <input v-model="form.expected_salary" class="w-full rounded-lg bg-navy-950/50 border border-navy-800/50 px-4 py-3 text-parchment placeholder-navy-500 focus:border-chart-400/50 focus:outline-none focus:ring-1 focus:ring-chart-400/20 transition-all" placeholder="e.g. $80,000" />
          </div>
          <div>
            <label class="flex items-center gap-2 text-xs font-mono text-navy-400 uppercase tracking-wider mb-1.5">
              <LanguageIcon class="h-3.5 w-3.5" />
              Languages <span class="normal-case font-mono text-navy-500 text-[10px]">(comma-sep)</span>
            </label>
            <input v-model="form.languages" class="w-full rounded-lg bg-navy-950/50 border border-navy-800/50 px-4 py-3 text-parchment placeholder-navy-500 focus:border-chart-400/50 focus:outline-none focus:ring-1 focus:ring-chart-400/20 transition-all" placeholder="English, French" />
          </div>
        </div>

        <!-- Resume Text -->
        <div>
          <label class="flex items-center gap-2 text-xs font-mono text-navy-400 uppercase tracking-wider mb-1.5">
            <DocumentTextIcon class="h-3.5 w-3.5" />
            Resume text <span class="normal-case font-mono text-navy-500 text-[10px]">(optional — paste it in)</span>
          </label>
          <textarea v-model="form.resume_text" rows="4" class="w-full rounded-lg bg-navy-950/50 border border-navy-800/50 px-4 py-3 text-parchment placeholder-navy-500 focus:border-chart-400/50 focus:outline-none focus:ring-1 focus:ring-chart-400/20 transition-all resize-y" placeholder="Paste your resume text here..." />
        </div>

        <!-- Error & Submit -->
        <div class="space-y-4">
          <p v-if="error" class="text-sm text-coral-400 flex items-center gap-2">
            <XCircleIcon class="h-4 w-4 flex-shrink-0" />
            {{ error }}
          </p>
          <button type="submit" class="inline-flex items-center gap-2 rounded-lg bg-chart-400/10 px-6 py-3 text-sm font-medium text-chart-400 border border-chart-400/20 hover:bg-chart-400/20 transition-all disabled:opacity-50 disabled:cursor-not-allowed" :disabled="saving">
            <ArrowPathIcon v-if="saving" class="h-4 w-4 animate-spin" />
            <SparklesIcon v-else class="h-4 w-4" />
            {{ saving ? "Generating your Opportunity DNA..." : "Save & Generate Opportunity DNA" }}
          </button>
        </div>
      </form>

      <!-- DNA Display -->
      <section v-if="dna" class="mt-8 rounded-xl bg-navy-900/40 border border-chart-400/20 p-5 sm:p-6 backdrop-blur-sm transition-all hover:border-chart-400/30">
        <div class="flex items-center gap-3 mb-4 pb-4 border-b border-navy-800/50">
          <div class="flex h-10 w-10 items-center justify-center rounded-lg bg-chart-400/10 border border-chart-400/20">
            <ShieldCheckIcon class="h-5 w-5 text-chart-400" />
          </div>
          <div>
            <p class="text-xs font-mono text-chart-400 uppercase tracking-wider">Your Opportunity DNA™</p>
            <p class="text-sm text-parchment font-medium">Profile Analysis Complete</p>
          </div>
          <CheckCircleIcon class="ml-auto h-5 w-5 text-chart-400" />
        </div>

        <p class="text-parchment leading-relaxed">{{ dna.summary }}</p>

        <div class="mt-6 grid gap-6 sm:grid-cols-2">
          <div class="rounded-lg bg-navy-950/50 border border-chart-400/10 p-4">
            <div class="flex items-center gap-2 mb-3">
              <CheckCircleIcon class="h-4 w-4 text-chart-400" />
              <h3 class="text-sm font-medium text-chart-400">Strengths</h3>
            </div>
            <ul class="space-y-1.5">
              <li v-for="s in dna.strengths" :key="s" class="flex items-start gap-2 text-sm text-navy-300">
                <span class="mt-1.5 h-1.5 w-1.5 rounded-full bg-chart-400/40 flex-shrink-0"></span>
                {{ s }}
              </li>
            </ul>
          </div>
          <div class="rounded-lg bg-navy-950/50 border border-coral-400/10 p-4">
            <div class="flex items-center gap-2 mb-3">
              <XCircleIcon class="h-4 w-4 text-coral-400" />
              <h3 class="text-sm font-medium text-coral-400">Watch-outs</h3>
            </div>
            <ul class="space-y-1.5">
              <li v-for="w in dna.weaknesses" :key="w" class="flex items-start gap-2 text-sm text-navy-300">
                <span class="mt-1.5 h-1.5 w-1.5 rounded-full bg-coral-400/40 flex-shrink-0"></span>
                {{ w }}
              </li>
            </ul>
          </div>
        </div>

        <!-- Recommended Categories -->
        <div class="mt-6">
          <p class="text-xs font-mono text-navy-400 uppercase tracking-wider mb-3">Recommended Categories</p>
          <div class="flex flex-wrap gap-2">
            <span v-for="c in dna.recommended_categories" :key="c" class="inline-flex items-center gap-1.5 rounded-full bg-chart-400/5 border border-chart-400/15 px-3 py-1.5 text-xs text-chart-400">
              <EyeIcon class="h-3 w-3" />
              {{ c }}
            </span>
          </div>
        </div>

        <NuxtLink to="/opportunities/find" class="inline-flex items-center gap-2 mt-6 rounded-lg bg-chart-400/10 px-5 py-2.5 text-sm font-medium text-chart-400 border border-chart-400/20 hover:bg-chart-400/20 transition-all">
          Find my opportunities
          <ArrowRightIcon class="h-4 w-4" />
        </NuxtLink>
      </section>

      <!-- Get my CV -->
      <section v-if="dna" class="mt-8 rounded-xl bg-navy-900/40 border border-navy-800/50 p-5 sm:p-6 backdrop-blur-sm transition-all hover:border-navy-700/70">
        <div class="flex items-center gap-3 mb-4 pb-4 border-b border-navy-800/50">
          <div class="flex h-10 w-10 items-center justify-center rounded-lg bg-chart-400/10 border border-chart-400/20">
            <DocumentArrowDownIcon class="h-5 w-5 text-chart-400" />
          </div>
          <div>
            <p class="text-xs font-mono text-chart-400 uppercase tracking-wider">Document generator</p>
            <p class="text-sm text-parchment font-medium">Get my CV</p>
          </div>
        </div>

        <label class="flex items-center gap-2 text-xs font-mono text-navy-400 uppercase tracking-wider mb-1.5">
          What should this CV portray about you?
        </label>
        <textarea
          v-model="cvDescription"
          rows="3"
          class="w-full rounded-lg bg-navy-950/50 border border-navy-800/50 px-4 py-3 text-parchment placeholder-navy-500 focus:border-chart-400/50 focus:outline-none focus:ring-1 focus:ring-chart-400/20 transition-all resize-y"
          placeholder="e.g. Emphasize my backend engineering skills for fintech roles, and highlight leadership experience"
        />
        <p class="mt-1.5 text-xs text-navy-500">
          Built only from what's in your profile above — nothing is invented, this just tells the AI what to emphasize.
        </p>

        <p v-if="cvError" class="mt-3 text-sm text-coral-400 flex items-center gap-2">
          <XCircleIcon class="h-4 w-4 flex-shrink-0" />
          {{ cvError }}
        </p>

        <button
          type="button"
          class="mt-4 inline-flex items-center gap-2 rounded-lg bg-chart-400/10 px-6 py-3 text-sm font-medium text-chart-400 border border-chart-400/20 hover:bg-chart-400/20 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
          :disabled="cvLoading"
          @click="generateAndDownloadCV"
        >
          <ArrowPathIcon v-if="cvLoading" class="h-4 w-4 animate-spin" />
          <DocumentArrowDownIcon v-else class="h-4 w-4" />
          {{ cvLoading ? "Building your CV..." : "Get my CV (PDF)" }}
        </button>
      </section>

      <!-- Get me a Cover Letter -->
      <section v-if="dna" class="mt-8 rounded-xl bg-navy-900/40 border border-navy-800/50 p-5 sm:p-6 backdrop-blur-sm transition-all hover:border-navy-700/70">
        <div class="flex items-center gap-3 mb-4 pb-4 border-b border-navy-800/50">
          <div class="flex h-10 w-10 items-center justify-center rounded-lg bg-signal-400/10 border border-signal-400/20">
            <EnvelopeIcon class="h-5 w-5 text-signal-400" />
          </div>
          <div>
            <p class="text-xs font-mono text-signal-400 uppercase tracking-wider">Document generator</p>
            <p class="text-sm text-parchment font-medium">Get me a cover letter</p>
          </div>
        </div>

        <label class="flex items-center gap-2 text-xs font-mono text-navy-400 uppercase tracking-wider mb-1.5">
          What should this cover letter portray about you?
        </label>
        <textarea
          v-model="coverDescription"
          rows="3"
          class="w-full rounded-lg bg-navy-950/50 border border-navy-800/50 px-4 py-3 text-parchment placeholder-navy-500 focus:border-signal-400/50 focus:outline-none focus:ring-1 focus:ring-signal-400/20 transition-all resize-y"
          placeholder="e.g. I'm applying for early-career roles and want to show enthusiasm plus hands-on project experience"
        />
        <p class="mt-1.5 text-xs text-navy-500">
          General-purpose by default. To target one opportunity specifically, generate this from that opportunity's page instead.
        </p>

        <p v-if="coverError" class="mt-3 text-sm text-coral-400 flex items-center gap-2">
          <XCircleIcon class="h-4 w-4 flex-shrink-0" />
          {{ coverError }}
        </p>

        <button
          type="button"
          class="mt-4 inline-flex items-center gap-2 rounded-lg bg-signal-400/10 px-6 py-3 text-sm font-medium text-signal-400 border border-signal-400/20 hover:bg-signal-400/20 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
          :disabled="coverLoading"
          @click="generateAndDownloadCoverLetter"
        >
          <ArrowPathIcon v-if="coverLoading" class="h-4 w-4 animate-spin" />
          <EnvelopeIcon v-else class="h-4 w-4" />
          {{ coverLoading ? "Writing your letter..." : "Get my cover letter (PDF)" }}
        </button>
      </section>
    </main>
  </div>
</template>