import { keyStore } from '@stardust-collective/dag4-keystore';

(async () => {
  const args = process.argv.slice(2);

  if (args.length < 2) {
    console.error('Usage: node script.js <uncompressedPublicKey> <txHash> <signature>');
    process.exit(1);
  }

  const uncompressedPublicKey = args[0];
  const txHash = args[1];
  const signature = args[2];

  try {
    const success = keyStore.verify(uncompressedPublicKey, txHash, signature);
    console.log(success);
  } catch (error) {
    console.error('Error during signing:', error.message || error);
  }
})();