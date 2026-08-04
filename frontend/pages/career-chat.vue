<script setup lang="ts">
const route = useRoute();
const api = useApi();

const sessionId = ref<string | null>((route.query.session_id as string) || null);
const opportunityId = ref<string | null>((route.query.opportunity_id as string) || null);
const messages = ref<{ role: string; content: string }[]>([]);
const input = ref("");
const sending = ref(false);
const error = ref("");
const sessions = ref<any[]>([]);
const loadingHistory = ref(false);

async function loadSessions() {
  try {
    sessions.value = await api.get("/chat/sessions");
  } catch (e) {
    // ignore
  }
}

async function loadSession(id: string) {
  loadingHistory.value = true;
  try {
    const msgs: any = await api.get(`/chat/sessions/${id}`);
    messages.value = msgs.map((m: any) => ({ role: m.role, content: m.content }));
    sessionId.value = id;
  } finally {
    loadingHistory.value = false;
  }
}

async function send() {
  if (!input.value.trim() || sending.value) return;
  const userMessage = input.value;
  input.value = "";
  error.value = "";
  messages.value.push({ role: "user", content: userMessage });
  sending.value = true;
  try {
    const res: any = await api.post("/chat", {
      session_id: sessionId.value,
      message: userMessage,
      opportunity_id: sessionId.value ? null : opportunityId.value,
    });
    sessionId.value = res.session_id;
    messages.value.push({ role: "assistant", content: res.reply });
    await loadSessions();
  } catch (e: any) {
    error.value = e?.data?.detail || "Couldn't send that. Try again.";
    messages.value.pop(); // remove the optimistic user bubble on failure
  } finally {
    sending.value = false;
  }
}

function newChat() {
  sessionId.value = null;
  opportunityId.value = null;
  messages.value = [];
}

onMounted(async () => {
  await loadSessions();
  if (sessionId.value) await loadSession(sessionId.value);
});
</script>

<template>
  <div>
    <AppNav />
    <main class="mx-auto flex max-w-5xl gap-6 px-6 py-12">
      <!-- Session list -->
      <aside class="hidden w-56 shrink-0 sm:block">
        <button class="btn-ghost w-full !py-2 text-sm" @click="newChat">+ New chat</button>
        <ul class="mt-4 space-y-1">
          <li v-for="s in sessions" :key="s.id">
            <button
              class="w-full truncate rounded-lg px-3 py-2 text-left text-sm transition-colors"
              :class="s.id === sessionId ? 'bg-navy-800 text-parchment' : 'text-navy-600 hover:text-parchment'"
              @click="loadSession(s.id)"
            >
              {{ s.title }}
            </button>
          </li>
        </ul>
      </aside>

      <!-- Chat -->
      <section class="flex min-h-[70vh] flex-1 flex-col">
        <p class="waypoint-label mb-2">Career chat</p>
        <h1 class="mb-6 text-2xl font-semibold text-parchment">Ask your AI career coach</h1>

        <div class="card flex flex-1 flex-col overflow-hidden">
          <div class="flex-1 space-y-4 overflow-y-auto pr-1">
            <p v-if="!messages.length && !loadingHistory" class="text-sm text-navy-600">
              Ask about your matches, tweak your roadmap, or get feedback on tone — this
              conversation remembers context as you go.
            </p>
            <div
              v-for="(m, i) in messages"
              :key="i"
              class="max-w-[85%] rounded-2xl px-4 py-3 text-sm"
              :class="m.role === 'user'
                ? 'ml-auto bg-signal/15 text-parchment'
                : 'mr-auto bg-navy-800/60 text-parchment'"
            >
              {{ m.content }}
            </div>
            <div v-if="sending" class="mr-auto max-w-[85%] rounded-2xl bg-navy-800/60 px-4 py-3 text-sm text-navy-600">
              Thinking...
            </div>
          </div>

          <p v-if="error" class="mt-3 text-sm text-coral">{{ error }}</p>

          <form class="mt-4 flex gap-2" @submit.prevent="send">
            <input
              v-model="input"
              class="input-field flex-1"
              placeholder="Ask a follow-up..."
              :disabled="sending"
            />
            <button type="submit" class="btn-beacon !px-5" :disabled="sending || !input.trim()">
              Send
            </button>
          </form>
        </div>
      </section>
    </main>
  </div>
</template>
