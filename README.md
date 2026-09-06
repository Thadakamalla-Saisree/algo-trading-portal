# ⚡ Algo Trading Labs — Commercial Portal & Licensing Server

Institutional Quantitative Trading Chrome Extensions:
1. **Polymarket BTC 5M Sniper Pro** ($10 USDT)
2. **Pocket Option Signal Pro** ($10 USDT)
3. **Pro Trader Dual VIP Bundle** ($18 USDT — Save $2)

---

## 🚀 Quick Start (Local Run)

```bash
# 1. Install dependencies
npm install

# 2. Start server
node server.js

# 3. Access Portal:
# Landing Page:    http://localhost:3000
# Admin Dashboard: http://localhost:3000/admin (Password: Saisree1722$)
```

---

## 🌐 Deploying Live to Render (Step-by-Step)

### Option 1: Render Blueprints (Recommended)
1. Push this repository to GitHub:
   ```bash
   git add .
   git commit -m "Deploy Algo Trading Portal"
   git branch -M main
   git remote add origin https://github.com/YOUR_USERNAME/algo-trading-portal.git
   git push -u origin main
   ```
2. Log in to [Render Dashboard](https://dashboard.render.com).
3. Click **New +** -> **Blueprint**.
4. Connect this GitHub repository.
5. Render reads `render.yaml` automatically and configures:
   - Service: Web Service (`Node.js`)
   - Build Command: `npm install`
   - Start Command: `node server.js`
   - Health Check: `/health`
6. Click **Apply**. Your website and licensing API are live in 60 seconds!

### Option 2: Standard Web Service
1. On Render, click **New +** -> **Web Service**.
2. Connect your GitHub repository.
3. Settings:
   - **Name**: `algo-trading-portal`
   - **Runtime**: `Node`
   - **Build Command**: `npm install`
   - **Start Command**: `node server.js`
4. Environment Variables:
   - `TRC20_ADDRESS`: `TLXS78k5X6cB9zQHzDQeh4NtTddmj7Z8L7`
   - `BEP20_ADDRESS`: `0x86c304c8015c1a51a520e66295ad75f85aa08b60`
   - `ADMIN_PASSWORD`: `Saisree1722$`
   - `JWT_SECRET`: `ALGO_QUANT_VIP_SECRET_9922883344_SAISREE_CRYPTO_AUTH`
5. Click **Create Web Service**.

---

## 📦 What Is Included

- **`public/index.html`**: Cyberpunk fintech dark landing page with:
  - Hero with real-time live pulse ribbon.
  - Polymarket BTC 5M Sniper deep dive with embedded 720p HD video player.
  - Pocket Option Signal Pro deep dive with embedded 720p HD video player.
  - Transparent pricing cards ($10 / $10 / $18 bundle).
  - Automated crypto checkout modal with on-chain TronGrid & BscScan verification.
  - Self-service license key lookup and re-download tool.
- **`public/admin.html`**: Owner dashboard (`Saisree1722$`) to view total revenue, active users, and issue 1-click manual lifetime keys.
- **`public/videos/`**: Pre-rendered HD walkthrough videos for both extensions with SAPI voiceover narration.
- **`public/downloads/`**: Pre-packaged `.zip` files for both extensions and the combined dual bundle.
- **`blockchain.js`**: Direct blockchain queries to Tronscan API (TRC-20) and Binance Smart Chain RPC (BEP-20).
- **`server.js`**: Express server managing crypto payments, JWT issuance, and file delivery.
