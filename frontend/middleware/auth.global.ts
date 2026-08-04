const PUBLIC_PATHS = ["/", "/login", "/signup"];

export default defineNuxtRouteMiddleware(async (to) => {
  if (import.meta.server) return;

  const { user, authReady, init } = useAuth();
  if (!authReady.value) await init();

  const isPublic = PUBLIC_PATHS.includes(to.path);
  if (!user.value && !isPublic) {
    return navigateTo("/login");
  }
  if (user.value && (to.path === "/login" || to.path === "/signup")) {
    return navigateTo("/dashboard");
  }
});
