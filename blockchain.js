const config = require('./config');

// Official USDT Contract Addresses
const TRON_USDT_CONTRACT = 'TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t';
const BSC_USDT_CONTRACT = '0x55d398326f99059ff775485246999027b3197955';

/**
 * Verify USDT TRC-20 transaction on the Tron blockchain
 * @param {string} txid - Tron transaction hash
 * @param {number} requiredUsdt - Required amount (e.g. 10.0 or 18.0)
 * @returns {Promise<{ success: boolean, message: string, amount?: number }>}
 */
async function verifyTronUSDT(txid, requiredUsdt = 10.0) {
  try {
    const cleanId = txid.trim();
    if (cleanId.length < 30) {
      return { success: false, message: 'Invalid Tron transaction hash length' };
    }

    const url = `https://apilist.tronscanapi.com/api/transaction-info?hash=${cleanId}`;
    const res = await fetch(url, { headers: { 'Accept': 'application/json' } });
    if (!res.ok) {
      return { success: false, message: 'Blockchain node query failed' };
    }

    const data = await res.json();
    if (!data || !data.hash) {
      return { success: false, message: 'Transaction not found on Tron blockchain yet. Please wait 15-30s for block confirmation.' };
    }

    if (data.confirmed !== true && data.contractRet !== 'SUCCESS') {
      return { success: false, message: 'Transaction is still unconfirmed or failed on Tron blockchain.' };
    }

    const trc20Transfers = data.trc20TransferInfo || [];
    let matchedTransfer = null;
    const targetRecipient = config.TRC20_ADDRESS.toLowerCase();

    for (const t of trc20Transfers) {
      const toAddr = (t.to_address || '').toLowerCase();
      const symbol = (t.symbol || '').toUpperCase();
      const contractAddr = (t.contract_address || '').trim();

      if (toAddr === targetRecipient && (symbol === 'USDT' || contractAddr === TRON_USDT_CONTRACT)) {
        matchedTransfer = t;
        break;
      }
    }

    if (!matchedTransfer) {
      return { 
        success: false, 
        message: `Transaction does not transfer TRC-20 USDT to recipient address (${config.TRC20_ADDRESS})` 
      };
    }

    const amountVal = parseFloat(matchedTransfer.amount_str || matchedTransfer.amount || 0) / 1000000;

    if (amountVal < (requiredUsdt - 0.05)) {
      console.warn(`[Tron Reject] Received ${amountVal.toFixed(2)} USDT, expected >= ${requiredUsdt} USDT`);
      return { 
        success: false, 
        message: `Payment Rejected: Sent amount (${amountVal.toFixed(2)} USDT) is LESS than the required ${requiredUsdt} USDT.` 
      };
    }

    console.log(`[Tron Success] Received ${amountVal.toFixed(2)} USDT (>= ${requiredUsdt} USDT)`);
    return { 
      success: true, 
      message: `Verified on Tron: Received ${amountVal.toFixed(2)} USDT`, 
      amount: amountVal 
    };
  } catch (e) {
    console.error('Tron verification error:', e);
    return { success: false, message: 'Tron network verification error: ' + e.message };
  }
}

/**
 * Verify USDT BEP-20 transaction on Binance Smart Chain
 * @param {string} txid - BSC transaction hash (0x...)
 * @param {number} requiredUsdt - Required amount (e.g. 10.0 or 18.0)
 * @returns {Promise<{ success: boolean, message: string, amount?: number }>}
 */
async function verifyBscUSDT(txid, requiredUsdt = 10.0) {
  try {
    let cleanId = txid.trim();
    if (!cleanId.startsWith('0x')) cleanId = '0x' + cleanId;
    if (cleanId.length !== 66) {
      return { success: false, message: 'Invalid BSC transaction hash format (must be 66 characters beginning with 0x)' };
    }

    const rpcRes = await fetch('https://bsc-dataseed.binance.org', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        jsonrpc: '2.0',
        method: 'eth_getTransactionReceipt',
        params: [cleanId],
        id: 1
      })
    });

    const rpcData = await rpcRes.json();
    const receipt = rpcData ? rpcData.result : null;

    if (!receipt) {
      return { success: false, message: 'Transaction not found on BSC blockchain yet. Please wait a few seconds and retry.' };
    }

    if (receipt.status !== '0x1') {
      return { success: false, message: 'Transaction was reverted or failed on BSC blockchain' };
    }

    const TRANSFER_TOPIC = '0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef';
    const targetAddressPadded = '0x000000000000000000000000' + config.BEP20_ADDRESS.substring(2).toLowerCase();

    let matchedLog = null;
    let transferAmount = 0;

    for (const log of (receipt.logs || [])) {
      const contractAddress = (log.address || '').toLowerCase();
      if (contractAddress !== BSC_USDT_CONTRACT.toLowerCase()) continue;

      if (log.topics && log.topics[0] === TRANSFER_TOPIC) {
        const toTopic = (log.topics[2] || '').toLowerCase();
        if (toTopic === targetAddressPadded) {
          matchedLog = log;
          const rawAmount = BigInt(log.data);
          transferAmount = Number(rawAmount / 10000000000000000n) / 100;
          break;
        }
      }
    }

    if (!matchedLog) {
      return { 
        success: false, 
        message: `Transaction does not transfer BEP-20 USDT to recipient address (${config.BEP20_ADDRESS})` 
      };
    }

    if (transferAmount < (requiredUsdt - 0.05)) {
      console.warn(`[BSC Reject] Received ${transferAmount.toFixed(2)} USDT, expected >= ${requiredUsdt} USDT`);
      return { 
        success: false, 
        message: `Payment Rejected: Sent amount (${transferAmount.toFixed(2)} USDT) is LESS than the required ${requiredUsdt} USDT.` 
      };
    }

    console.log(`[BSC Success] Received ${transferAmount.toFixed(2)} USDT (>= ${requiredUsdt} USDT)`);
    return { 
      success: true, 
      message: `Verified on BSC: Received ${transferAmount.toFixed(2)} USDT`, 
      amount: transferAmount 
    };
  } catch (e) {
    console.error('BSC verification error:', e);
    return { success: false, message: 'BSC verification error: ' + e.message };
  }
}

module.exports = {
  verifyTronUSDT,
  verifyBscUSDT
};
