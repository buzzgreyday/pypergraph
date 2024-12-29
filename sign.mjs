import { keyStore } from '@stardust-collective/dag4-keystore';

(async () => {
  const args = process.argv.slice(2);

  if (args.length < 2) {
    console.error('Usage: node script.js <privateKeyHex> <txHash>');
    process.exit(1);
  }

  const privateKeyHex = args[0];
  const txHash = args[1];

  try {
    const signature = await keyStore.sign(privateKeyHex, txHash);
    console.log(signature);
  } catch (error) {
    console.error('Error during signing:', error.message || error);
  }
})();


