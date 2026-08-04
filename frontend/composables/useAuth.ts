import type { Session, User } from "@supabase/supabase-js";

const user = ref<User | null>(null);
const session = ref<Session | null>(null);
const authReady = ref(false);

export function useAuth() {
  const { $supabase } = useNuxtApp();

  async function init() {
    if (authReady.value) return;
    const { data } = await $supabase.auth.getSession();
    session.value = data.session;
    user.value = data.session?.user ?? null;
    authReady.value = true;

    $supabase.auth.onAuthStateChange((_event, newSession) => {
      session.value = newSession;
      user.value = newSession?.user ?? null;
    });
  }

  async function signUp(email: string, password: string) {
    const { data, error } = await $supabase.auth.signUp({ email, password });
    if (error) throw error;
    return data;
  }

  async function signIn(email: string, password: string) {
    const { data, error } = await $supabase.auth.signInWithPassword({ email, password });
    if (error) throw error;
    return data;
  }

  async function signInWithGoogle() {
    const { error } = await $supabase.auth.signInWithOAuth({
      provider: "google",
      options: { redirectTo: `${window.location.origin}/dashboard` },
    });
    if (error) throw error;
  }

  async function signOut() {
    await $supabase.auth.signOut();
    user.value = null;
    session.value = null;
    await navigateTo("/login");
  }

  function accessToken() {
    return session.value?.access_token ?? null;
  }

  return { user, session, authReady, init, signUp, signIn, signInWithGoogle, signOut, accessToken };
}
