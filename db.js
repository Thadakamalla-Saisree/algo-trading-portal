const fs = require('fs');
const path = require('path');

const DB_FILE = path.join(__dirname, 'database.json');

// Initialize database file if it does not exist
if (!fs.existsSync(DB_FILE)) {
  fs.writeFileSync(DB_FILE, JSON.stringify({ users: [], usedTxids: [] }, null, 2));
}

function readData() {
  try {
    const raw = fs.readFileSync(DB_FILE, 'utf8');
    return JSON.parse(raw);
  } catch (e) {
    return { users: [], usedTxids: [] };
  }
}

function writeData(data) {
  try {
    fs.writeFileSync(DB_FILE, JSON.stringify(data, null, 2));
    return true;
  } catch (e) {
    console.error('Failed to write database:', e);
    return false;
  }
}

function getUserByEmail(email) {
  if (!email) return null;
  const data = readData();
  return data.users.find(u => u.email.toLowerCase() === email.trim().toLowerCase()) || null;
}

function createUser(email, passwordHash, deviceId) {
  const data = readData();
  const cleanEmail = email.trim().toLowerCase();
  const existing = data.users.find(u => u.email.toLowerCase() === cleanEmail);
  if (existing) return existing;

  const newUser = {
    id: 'usr_' + Date.now() + '_' + Math.random().toString(36).substring(2, 7),
    email: cleanEmail,
    passwordHash: passwordHash,
    deviceId: deviceId || '',
    licenses: [],
    registeredAt: new Date().toISOString()
  };

  data.users.push(newUser);
  writeData(data);
  return newUser;
}

function addLicense(email, product, network, txid, licenseKey, token, amount) {
  const data = readData();
  const cleanEmail = email.trim().toLowerCase();
  let user = data.users.find(u => u.email.toLowerCase() === cleanEmail);
  
  if (!user) {
    user = {
      id: 'usr_' + Date.now() + '_' + Math.random().toString(36).substring(2, 7),
      email: cleanEmail,
      passwordHash: null,
      deviceId: '',
      licenses: [],
      registeredAt: new Date().toISOString()
    };
    data.users.push(user);
  }

  if (!user.licenses) user.licenses = [];

  const licenseRecord = {
    id: 'lic_' + Date.now() + '_' + Math.random().toString(36).substring(2, 7),
    product: product, // POLYMARKET_5M, POCKET_OPTION_1M, DUAL_BUNDLE
    licenseKey: licenseKey,
    token: token,
    network: network || 'MANUAL_APPROVAL',
    txid: txid || 'DIRECT_ISSUE',
    amount: amount || 10.0,
    issuedAt: new Date().toISOString(),
    isActive: true
  };

  user.licenses.push(licenseRecord);

  if (txid && txid !== 'DIRECT_ISSUE' && !data.usedTxids.includes(txid.toLowerCase())) {
    data.usedTxids.push(txid.toLowerCase());
  }

  writeData(data);
  return { user, license: licenseRecord };
}

function getLicenseByKey(licenseKey) {
  if (!licenseKey) return null;
  const cleanKey = licenseKey.trim().toUpperCase();
  const data = readData();
  
  for (const user of data.users) {
    for (const lic of (user.licenses || [])) {
      if ((lic.licenseKey && lic.licenseKey.toUpperCase() === cleanKey) || lic.token === licenseKey) {
        return { user, license: lic };
      }
    }
  }
  return null;
}

function revokeLicense(email, licenseKey) {
  const data = readData();
  const cleanEmail = email.trim().toLowerCase();
  const user = data.users.find(u => u.email.toLowerCase() === cleanEmail);
  if (!user || !user.licenses) return false;

  let revoked = false;
  for (const lic of user.licenses) {
    if (!licenseKey || lic.licenseKey === licenseKey || lic.token === licenseKey) {
      lic.isActive = false;
      revoked = true;
    }
  }

  if (revoked) writeData(data);
  return revoked;
}

function getAllUsers() {
  const data = readData();
  return data.users.map(u => ({
    id: u.id,
    email: u.email,
    registeredAt: u.registeredAt,
    licenseCount: (u.licenses || []).filter(l => l.isActive).length,
    licenses: u.licenses || []
  }));
}

function isTxidClaimed(txid) {
  if (!txid) return false;
  const data = readData();
  return data.usedTxids.includes(txid.trim().toLowerCase());
}

module.exports = {
  getUserByEmail,
  createUser,
  addLicense,
  getLicenseByKey,
  revokeLicense,
  getAllUsers,
  isTxidClaimed
};
