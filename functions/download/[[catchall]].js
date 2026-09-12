export async function onRequest(context) {
  const url = new URL(context.request.url);
  const target = 'https://algo-trading-portal.onrender.com' + url.pathname + url.search;
  return fetch(new Request(target, context.request));
}