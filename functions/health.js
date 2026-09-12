export async function onRequest() {
  return new Response(JSON.stringify({ status: 'ok', service: 'AlgoTrading-Portal-Cloudflare-Edge', edge: true }), {
    headers: { 'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*' }
  });
}