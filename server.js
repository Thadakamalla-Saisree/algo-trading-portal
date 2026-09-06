const express = require('express');
const cors = require('cors');
const path = require('path');
const bcrypt = require('bcryptjs');
const jwt = require('jsonwebtoken');

const config = require('./config');
const db = require('./db');
const blockchain = require('./blockchain');

const app = express();

app.use(cors());
app.use(express.json());
app.use(express.static(path.join(__dirname, 'public')));

// Generate Human-Readable License Key
function generateLicenseKey(product) {
  const prefix = product === 'POLYMARKET_5M' ? 'POLY-VIP' 
               : product === 'POCKET_OPTION_1M' ? 'POCKET-VIP' 
               : 'DUAL-VIP';
  const part1 = Math.random().toString(36).substring(2, 6).toUpperCase();
  const part2 = Math.random().toString(36).substring(2, 6).toUpperCase();
  const part3 = Date.now().toString(36).slice(-4).toUpperCase();
  return `${prefix}-${part1}-${part2}-${part3}`;
}

// Generate Signed Tamper-Proof License JWT
function issueLicenseToken(email, product, licenseKey) {
  return jwt.sign(
    {
      email,
      product,
      licenseKey,
      isPaid: true,
      issuedAt: Date.now()
    },
    config.JWT_SECRET,
    { expiresIn: '3650d' } // Lifetime 10 years
  );
}

// 1. Health Check for Render
app.get('/health', (req, res) => {
  res.json({ status: 'ok', service: 'Algo Trading Portal API', uptime: process.uptime() });
});

// 2. Public Payment Configuration & Pricing
app.get('/api/config', (req, res) => {
  res.json({
    trc20Address: config.TRC20_ADDRESS,
    bep20Address: config.BEP20_ADDRESS,
    pricing: config.PRICING
  });
});

// 3. User Registration
app.post('/api/register', async (req, res) => {
  try {
    const { email, password, deviceId } = req.body;
    if (!email || !password) {
      return res.status(400).json({ error: 'Email and password are required' });
    }

    const existing = db.getUserByEmail(email);
    if (existing && existing.passwordHash) {
      return res.status(400).json({ error: 'Email is already registered. Please log in.' });
    }

    const salt = await bcrypt.genSalt(10);
    const hash = await bcrypt.hash(password, salt);

    const user = db.createUser(email, hash, deviceId);
    res.json({
      success: true,
      message: 'Account registered successfully',
      user: {
        id: user.id,
        email: user.email,
        licenseCount: (user.licenses || []).length
      }
    });
  } catch (err) {
    res.status(500).json({ error: 'Server registration error: ' + err.message });
  }
});

// 4. User Login
app.post('/api/login', async (req, res) => {
  try {
    const { email, password } = req.body;
    if (!email || !password) {
      return res.status(400).json({ error: 'Email and password are required' });
    }

    const user = db.getUserByEmail(email);
    if (!user) {
      return res.status(404).json({ error: 'User account not found. Please register first.' });
    }

    if (!user.passwordHash) {
      return res.status(400).json({ error: 'Account created via direct deposit. Please request a password reset or enter license key.' });
    }

    const isMatch = await bcrypt.compare(password, user.passwordHash);
    if (!isMatch) {
      return res.status(401).json({ error: 'Incorrect password' });
    }

    const activeLicenses = (user.licenses || []).filter(l => l.isActive);
    const primaryToken = activeLicenses.length > 0 ? activeLicenses[0].token : null;

    res.json({
      success: true,
      user: {
        id: user.id,
        email: user.email,
        isPaid: activeLicenses.length > 0,
        licenseCount: activeLicenses.length,
        licenses: activeLicenses
      },
      licenseToken: primaryToken
    });
  } catch (err) {
    res.status(500).json({ error: 'Login error: ' + err.message });
  }
});

// 5. Submit & Verify Crypto Payment (TxID)
app.post('/api/submit-payment', async (req, res) => {
  try {
    const { email, network, txid, product = 'POLYMARKET_5M' } = req.body;
    if (!email || !network || !txid) {
      return res.status(400).json({ error: 'Email, network, and transaction hash (TxID) are required' });
    }

    const cleanTxid = txid.trim();
    if (db.isTxidClaimed(cleanTxid)) {
      return res.status(400).json({ 
        error: 'This Transaction Hash (TxID) has already been claimed!' 
      });
    }

    // Determine required price based on product
    const targetProduct = ['POLYMARKET_5M', 'POCKET_OPTION_1M', 'DUAL_BUNDLE'].includes(product)
      ? product
      : 'POLYMARKET_5M';

    const requiredAmount = config.PRICING[targetProduct] || 10.0;

    // Verify On-Chain
    let verifyResult = null;
    const netUpper = network.toUpperCase();
    if (netUpper === 'TRC20' || netUpper.includes('TRON')) {
      verifyResult = await blockchain.verifyTronUSDT(cleanTxid, requiredAmount);
    } else if (netUpper === 'BEP20' || netUpper.includes('BSC') || netUpper.includes('BNB')) {
      verifyResult = await blockchain.verifyBscUSDT(cleanTxid, requiredAmount);
    } else {
      return res.status(400).json({ error: 'Unsupported network. Use TRC20 or BEP20.' });
    }

    if (!verifyResult || !verifyResult.success) {
      return res.status(400).json({
        error: verifyResult ? verifyResult.message : 'Blockchain verification failed'
      });
    }

    // Issue License
    const licenseKey = generateLicenseKey(targetProduct);
    const token = issueLicenseToken(email, targetProduct, licenseKey);
    const { user, license } = db.addLicense(
      email, 
      targetProduct, 
      netUpper, 
      cleanTxid, 
      licenseKey, 
      token, 
      verifyResult.amount || requiredAmount
    );

    res.json({
      success: true,
      message: `Payment verified on-chain (${verifyResult.amount} USDT)! Lifetime Pro License unlocked.`,
      product: targetProduct,
      licenseKey: licenseKey,
      licenseToken: token,
      amountReceived: verifyResult.amount,
      downloadUrl: targetProduct === 'POLYMARKET_5M' ? '/download/polymarket-extension.zip'
                 : targetProduct === 'POCKET_OPTION_1M' ? '/download/pocket-option-extension.zip'
                 : '/download/dual-bundle.zip'
    });
  } catch (err) {
    res.status(500).json({ error: 'Payment processing error: ' + err.message });
  }
});

// 6. Verify License Key (Human format e.g. POLY-VIP-XXXX)
app.post('/api/verify-key', (req, res) => {
  try {
    const { licenseKey, email, product } = req.body;
    if (!licenseKey) return res.status(400).json({ valid: false, error: 'License key missing' });

    const match = db.getLicenseByKey(licenseKey);
    if (match && match.license.isActive) {
      // Check product compatibility
      const licProd = match.license.product;
      const isCompatible = licProd === 'DUAL_BUNDLE' || !product || licProd === product;

      if (!isCompatible) {
        return res.json({ 
          valid: false, 
          error: `License key belongs to ${licProd}, not compatible with requested ${product}` 
        });
      }

      return res.json({
        valid: true,
        email: match.user.email,
        product: licProd,
        licenseKey: match.license.licenseKey,
        token: match.license.token,
        issuedAt: match.license.issuedAt
      });
    }

    // Direct JWT token verification fallback
    jwt.verify(licenseKey, config.JWT_SECRET, (err, decoded) => {
      if (err) {
        return res.json({ valid: false, error: 'Invalid or expired license key/token' });
      }
      res.json({
        valid: true,
        email: decoded.email,
        product: decoded.product || 'PRO_VIP',
        token: licenseKey
      });
    });
  } catch (e) {
    res.json({ valid: false, error: e.message });
  }
});

// 7. Verify JWT License Token (Extension background check)
app.post('/api/verify-token', (req, res) => {
  try {
    const { token, product } = req.body;
    if (!token) return res.status(400).json({ valid: false, error: 'Token missing' });

    jwt.verify(token, config.JWT_SECRET, (err, decoded) => {
      if (err) {
        // Check if token string happens to be a valid license key
        const match = db.getLicenseByKey(token);
        if (match && match.license.isActive) {
          return res.json({
            valid: true,
            email: match.user.email,
            product: match.license.product
          });
        }
        return res.json({ valid: false, error: 'Token signature invalid or expired' });
      }

      // Check DB revocation
      const match = db.getLicenseByKey(decoded.licenseKey || token);
      if (match && !match.license.isActive) {
        return res.json({ valid: false, error: 'License has been revoked' });
      }

      res.json({
        valid: true,
        email: decoded.email,
        product: decoded.product,
        expiresAt: 'LIFETIME'
      });
    });
  } catch (e) {
    res.json({ valid: false, error: e.message });
  }
});

// 8. Self-Service License Lookup by Email
app.post('/api/license/lookup', (req, res) => {
  try {
    const { email } = req.body;
    if (!email) return res.status(400).json({ error: 'Email required' });

    const user = db.getUserByEmail(email);
    if (!user || !user.licenses || user.licenses.length === 0) {
      return res.status(404).json({ error: 'No licenses found for this email address.' });
    }

    const activeList = user.licenses.filter(l => l.isActive).map(l => ({
      product: l.product,
      licenseKey: l.licenseKey,
      issuedAt: l.issuedAt,
      network: l.network,
      downloadUrl: l.product === 'POLYMARKET_5M' ? '/download/polymarket-extension.zip'
                 : l.product === 'POCKET_OPTION_1M' ? '/download/pocket-option-extension.zip'
                 : '/download/dual-bundle.zip'
    }));

    res.json({
      success: true,
      email: user.email,
      licenses: activeList
    });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// =============================================================================
// DIRECT DOWNLOAD ENDPOINTS
// =============================================================================
app.get('/download/polymarket-extension.zip', (req, res) => {
  const file = path.join(__dirname, 'public', 'downloads', 'polymarket-btc-sniper.zip');
  res.download(file, 'polymarket-btc-sniper-pro.zip');
});

app.get('/download/pocket-option-extension.zip', (req, res) => {
  const file = path.join(__dirname, 'public', 'downloads', 'pocket-signal-pro.zip');
  res.download(file, 'pocket-signal-pro.zip');
});

app.get('/download/dual-bundle.zip', (req, res) => {
  const file = path.join(__dirname, 'public', 'downloads', 'algo-trading-dual-bundle.zip');
  res.download(file, 'algo-trading-pro-dual-bundle.zip');
});

app.get('/download/polymarket-video.mp4', (req, res) => {
  const file = path.join(__dirname, 'public', 'videos', 'polymarket-sniper-walkthrough.mp4');
  res.download(file, 'polymarket-sniper-walkthrough.mp4');
});

app.get('/download/pocket-option-video.mp4', (req, res) => {
  const file = path.join(__dirname, 'public', 'videos', 'pocket-signal-pro-walkthrough.mp4');
  res.download(file, 'pocket-signal-pro-walkthrough.mp4');
});

// =============================================================================
// ADMIN DASHBOARD (PROTECTED BY Saisree1722$)
// =============================================================================
function checkAdminAuth(req, res, next) {
  const pwd = req.headers['x-admin-password'];
  if (pwd === config.ADMIN_PASSWORD) {
    next();
  } else {
    res.status(403).json({ error: 'Unauthorized: Incorrect Admin Password' });
  }
}

app.post('/api/admin/login', (req, res) => {
  const { password } = req.body;
  if (password === config.ADMIN_PASSWORD) {
    res.json({ success: true, message: 'Admin authenticated' });
  } else {
    res.status(401).json({ error: 'Invalid admin password' });
  }
});

app.get('/api/admin/users', checkAdminAuth, (req, res) => {
  const users = db.getAllUsers();
  let totalRevenue = 0;
  let polyCount = 0;
  let poCount = 0;
  let dualCount = 0;

  users.forEach(u => {
    (u.licenses || []).forEach(l => {
      if (l.isActive) {
        totalRevenue += l.amount || (config.PRICING[l.product] || 10);
        if (l.product === 'POLYMARKET_5M') polyCount++;
        else if (l.product === 'POCKET_OPTION_1M') poCount++;
        else if (l.product === 'DUAL_BUNDLE') dualCount++;
      }
    });
  });

  res.json({
    stats: {
      totalUsers: users.length,
      totalRevenueUsdt: totalRevenue,
      polyCount,
      poCount,
      dualCount
    },
    users
  });
});

app.post('/api/admin/create-license', checkAdminAuth, (req, res) => {
  const { email, product = 'POLYMARKET_5M' } = req.body;
  if (!email) return res.status(400).json({ error: 'Email required' });

  const licenseKey = generateLicenseKey(product);
  const token = issueLicenseToken(email, product, licenseKey);
  const amount = config.PRICING[product] || 10.0;

  const { user, license } = db.addLicense(
    email,
    product,
    'MANUAL_ADMIN',
    'MANUAL_ADMIN_' + Date.now(),
    licenseKey,
    token,
    amount
  );

  res.json({
    success: true,
    message: `License created for ${email}`,
    licenseKey,
    token,
    product
  });
});

app.post('/api/admin/revoke', checkAdminAuth, (req, res) => {
  const { email, licenseKey } = req.body;
  if (!email) return res.status(400).json({ error: 'Email required' });

  const ok = db.revokeLicense(email, licenseKey);
  res.json({ success: ok, message: `Revocation status for ${email}` });
});

app.get('/admin', (req, res) => {
  res.sendFile(path.join(__dirname, 'public', 'admin.html'));
});

// Start Server
app.listen(config.PORT, () => {
  console.log(`\n========================================================`);
  console.log(`🚀 Algo Trading Unified Portal Server Active!`);
  console.log(`📡 URL: http://localhost:${config.PORT}`);
  console.log(`🔐 Admin Panel: http://localhost:${config.PORT}/admin`);
  console.log(`========================================================\n`);
});
