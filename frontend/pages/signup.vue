<script setup lang="ts">
import { ref } from 'vue';
import {
  EnvelopeIcon,
  LockClosedIcon,
  ArrowLeftIcon,
  UserPlusIcon,
  SparklesIcon,
  XCircleIcon,
  CheckCircleIcon,
  FingerPrintIcon
} from '@heroicons/vue/24/outline';
import { EyeIcon, EyeSlashIcon } from '@heroicons/vue/24/solid';

definePageMeta({ layout: false });

const { signUp, signInWithGoogle } = useAuth();
const email = ref("");
const password = ref("");
const error = ref("");
const loading = ref(false);
const done = ref(false);
const showPassword = ref(false);
const acceptTerms = ref(false);

async function onSubmit() {
  error.value = "";
  loading.value = true;
  try {
    await signUp(email.value, password.value);
    done.value = true;
  } catch (e: any) {
    error.value = e?.message || "Couldn't create your account. Try again.";
  } finally {
    loading.value = false;
  }
}
</script>

<template>
  <div class="relative min-h-screen bg-navy-950 flex items-center justify-center px-4 overflow-hidden">
    <!-- Subtle Background Pattern -->
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
      <div class="absolute top-1/4 -left-20 h-64 w-64 rounded-full bg-signal-400/5 blur-3xl"></div>
      <div class="absolute bottom-1/4 -right-20 h-64 w-64 rounded-full bg-chart-400/5 blur-3xl"></div>
    </div>

    <div class="relative z-10 w-full max-w-md">
      <!-- Back Link -->
      <NuxtLink to="/" class="group inline-flex items-center gap-2 text-sm text-navy-400 hover:text-parchment transition-colors mb-6">
        <ArrowLeftIcon class="h-4 w-4 group-hover:-translate-x-0.5 transition-transform" />
        Back home
      </NuxtLink>

      <!-- Card -->
      <div class="rounded-2xl bg-navy-900/40 border border-navy-800/50 p-6 sm:p-8 backdrop-blur-sm transition-all hover:border-navy-700/70">
        
        <!-- Success State -->
        <template v-if="done">
          <div class="flex items-center gap-3 mb-4">
            <div class="flex h-12 w-12 items-center justify-center rounded-full bg-chart-400/10 border border-chart-400/20">
              <CheckCircleIcon class="h-6 w-6 text-chart-400" />
            </div>
            <div>
              <span class="text-lg font-display font-medium text-parchment">Check your inbox</span>
            </div>
          </div>
          <p class="text-sm text-navy-300 leading-relaxed">
            We sent a confirmation link to <strong class="text-parchment">{{ email }}</strong>.
            Confirm your email, then sign in to build your profile and start your journey.
          </p>
          <div class="mt-6 p-4 rounded-lg bg-navy-950/50 border border-navy-800/50">
            <p class="text-xs text-navy-400 flex items-center gap-2">
              <SparklesIcon class="h-3.5 w-3.5 text-chart-400" />
              <span>Didn't receive the email? Check your spam folder or </span>
              <button class="text-chart-400 hover:text-chart-300 transition-colors">resend</button>
            </p>
          </div>
          <NuxtLink to="/login" class="inline-flex items-center justify-center gap-2 w-full mt-6 rounded-lg bg-chart-400/10 px-6 py-3 text-sm font-medium text-chart-400 border border-chart-400/20 hover:bg-chart-400/20 transition-all">
            <ArrowLeftIcon class="h-4 w-4" />
            Go to sign in
          </NuxtLink>
        </template>

        <!-- Form State -->
        <template v-else>
          <!-- Logo Area -->
          <div class="flex items-center gap-2 mb-6">
            <div class="flex h-10 w-10 items-center justify-center rounded-lg bg-chart-400/10 border border-chart-400/20">
              <FingerPrintIcon class="h-5 w-5 text-chart-400" />
            </div>
            <div>
              <span class="text-lg font-display font-medium text-parchment">CityOS</span>
              <span class="ml-1 rounded-full bg-chart-400/10 px-1.5 py-0.5 text-[8px] font-mono font-medium uppercase tracking-widest text-chart-400 border border-chart-400/10">AI</span>
            </div>
          </div>

          <h1 class="text-2xl font-display font-medium text-parchment tracking-tight">Chart your course</h1>
          <p class="mt-1.5 text-sm text-navy-400">Create an account to build your Opportunity DNA</p>

          <!-- Form -->
          <form class="mt-6 space-y-4" @submit.prevent="onSubmit">
            <div>
              <label class="flex items-center gap-2 text-xs font-mono text-navy-400 uppercase tracking-wider mb-1.5">
                <EnvelopeIcon class="h-3.5 w-3.5" />
                Email
              </label>
              <input 
                v-model="email" 
                type="email" 
                required 
                class="w-full rounded-lg bg-navy-950/50 border border-navy-800/50 px-4 py-3 text-parchment placeholder-navy-500 focus:border-chart-400/50 focus:outline-none focus:ring-1 focus:ring-chart-400/20 transition-all" 
                placeholder="you@example.com"
              />
            </div>

            <div>
              <label class="flex items-center gap-2 text-xs font-mono text-navy-400 uppercase tracking-wider mb-1.5">
                <LockClosedIcon class="h-3.5 w-3.5" />
                Password
              </label>
              <div class="relative">
                <input 
                  v-model="password" 
                  :type="showPassword ? 'text' : 'password'" 
                  required 
                  minlength="6"
                  class="w-full rounded-lg bg-navy-950/50 border border-navy-800/50 px-4 py-3 text-parchment placeholder-navy-500 focus:border-chart-400/50 focus:outline-none focus:ring-1 focus:ring-chart-400/20 transition-all pr-12" 
                  placeholder="At least 6 characters"
                />
                <button 
                  type="button"
                  @click="showPassword = !showPassword"
                  class="absolute right-3 top-1/2 -translate-y-1/2 text-navy-500 hover:text-parchment transition-colors"
                >
                  <EyeIcon v-if="!showPassword" class="h-4 w-4" />
                  <EyeSlashIcon v-else class="h-4 w-4" />
                </button>
              </div>
              <div class="mt-2 flex items-center gap-2">
                <div class="h-1 flex-1 rounded-full bg-navy-800/50 overflow-hidden">
                  <div class="h-full rounded-full transition-all duration-300" :class="{
                    'bg-coral-400': password.length < 3,
                    'bg-signal-400': password.length >= 3 && password.length < 6,
                    'bg-chart-400': password.length >= 6
                  }" :style="{ width: Math.min((password.length / 10) * 100, 100) + '%' }"></div>
                </div>
                <span class="text-[10px] font-mono text-navy-500">{{ password.length }}/6+</span>
              </div>
            </div>

            <!-- Terms -->
            <label class="flex items-start gap-2.5 text-xs text-navy-400 cursor-pointer">
              <input 
                v-model="acceptTerms" 
                type="checkbox" 
                required
                class="mt-0.5 rounded border-navy-700 bg-navy-950 text-chart-400 focus:ring-chart-400/20" 
              />
              <span>I agree to the <NuxtLink to="/terms" class="text-chart-400 hover:text-chart-300 transition-colors">Terms of Service</NuxtLink> and <NuxtLink to="/privacy" class="text-chart-400 hover:text-chart-300 transition-colors">Privacy Policy</NuxtLink></span>
            </label>

            <!-- Error -->
            <div v-if="error" class="rounded-lg bg-coral-400/5 border border-coral-400/20 p-3 flex items-start gap-2.5">
              <XCircleIcon class="h-4 w-4 text-coral-400 flex-shrink-0 mt-0.5" />
              <p class="text-sm text-coral-400">{{ error }}</p>
            </div>

            <button 
              type="submit" 
              class="inline-flex items-center justify-center gap-2 w-full rounded-lg bg-chart-400/10 px-6 py-3 text-sm font-medium text-chart-400 border border-chart-400/20 hover:bg-chart-400/20 transition-all disabled:opacity-50 disabled:cursor-not-allowed" 
              :disabled="loading || !acceptTerms"
            >
              <UserPlusIcon v-if="!loading" class="h-4 w-4" />
              <div v-else class="h-4 w-4 animate-spin rounded-full border-2 border-chart-400 border-t-transparent"></div>
              {{ loading ? "Creating account..." : "Create account" }}
            </button>
          </form>

          <!-- Divider -->
          <div class="my-6 flex items-center gap-3">
            <div class="h-px flex-1 bg-navy-800/50" />
            <span class="text-xs text-navy-500">or continue with</span>
            <div class="h-px flex-1 bg-navy-800/50" />
          </div>

          <!-- Google Button -->
          <button 
            class="inline-flex items-center justify-center gap-3 w-full rounded-lg bg-navy-800/30 px-6 py-3 text-sm font-medium text-parchment border border-navy-700/50 hover:bg-navy-800/50 hover:border-navy-700/70 transition-all"
            @click="signInWithGoogle"
          >
            <svg class="h-5 w-5" viewBox="0 0 24 24">
              <path d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92a5.06 5.06 0 0 1-2.2 3.32v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.1z" fill="#4285F4"/>
              <path d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" fill="#34A853"/>
              <path d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z" fill="#FBBC05"/>
              <path d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" fill="#EA4335"/>
            </svg>
            Continue with Google
          </button>

          <!-- Footer -->
          <p class="mt-6 text-center text-sm text-navy-400">
            Already have an account?
            <NuxtLink to="/login" class="text-chart-400 hover:text-chart-300 transition-colors font-medium">
              Sign in
            </NuxtLink>
          </p>
        </template>
      </div>
    </div>
  </div>
</template>