/**
 * Algo Trading Portal - Unified Commercial Licensing & Payment Configuration
 */
module.exports = {
  PORT: process.env.PORT || 3000,
  
  // Binance USDT Deposit Addresses provided by owner
  TRC20_ADDRESS: process.env.TRC20_ADDRESS || 'TLXS78k5X6cB9zQHzDQeh4NtTddmj7Z8L7',
  BEP20_ADDRESS: process.env.BEP20_ADDRESS || '0x86c304c8015c1a51a520e66295ad75f85aa08b60',

  // Product Pricing
  PRICING: {
    POLYMARKET_5M: 10.0,
    POCKET_OPTION_1M: 10.0,
    DUAL_BUNDLE: 18.0
  },

  // Owner Admin Password
  ADMIN_PASSWORD: process.env.ADMIN_PASSWORD || 'Saisree1722$',

  // Anti-tamper JWT Secret
  JWT_SECRET: process.env.JWT_SECRET || 'ALGO_QUANT_VIP_SECRET_9922883344_SAISREE_CRYPTO_AUTH'
};
