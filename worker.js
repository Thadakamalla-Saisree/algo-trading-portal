export default {
  async fetch(request, env) {
    const url = new URL(request.url);

    // 1. Route API requests to Render backend
    if (url.pathname.startsWith('/api/')) {
      const target = 'https://algo-trading-portal.onrender.com' + url.pathname + url.search;
      return fetch(new Request(target, request));
    }

    // 2. Health check
    if (url.pathname === '/health') {
      const target = 'https://algo-trading-portal.onrender.com/health';
      return fetch(new Request(target, request));
    }

    // 3. Serve static assets via Cloudflare Assets binding
    return env.ASSETS.fetch(request);
  }
};
