import * as secp from '@noble/secp256k1';
import * as jsSha512 from 'js-sha512';
import { hmac } from '@noble/hashes/hmac';
import { sha256 } from '@noble/hashes/sha256';

(async () => {
  secp.etc.hmacSha256Sync = (k, ...m) => hmac(sha256, k, secp.etc.concatBytes(...m));
  const args = process.argv.slice(2);

  if (args.length < 2) {
    console.log('Usage: node script.js <privateKeyHex> <txHash>');
    process.exit(1);
  }

  const privateKeyHex = args[0];
  const txHash = args[1];

  // Convert the private key hex to a Buffer (ensure it's 32 bytes for secp256k1)
  const privateKey = Buffer.from(privateKeyHex, 'hex');

  if (privateKey.length !== 32) {
    console.error('Invalid private key length. It should be 32 bytes.');
    process.exit(1);
  }

  // Calculate the SHA512 hash of the transaction hash
  const sha512HashHex = jsSha512.sha512(txHash); // This returns a hex string

  // Convert the SHA512 hash (hex string) into a Buffer
  const sha512Hash = Buffer.from(sha512HashHex, 'hex');

  try {
    // Sign the SHA512 hash using the private key
    const sig = await secp.sign(sha512Hash, privateKey);

    // Convert the r and s values to hex and ensure they are padded to 32 bytes
    const rHex = sig.r.toString(16).padStart(64, '0'); // Ensure 32 bytes
    const sHex = sig.s.toString(16).padStart(64, '0'); // Ensure 32 bytes

    // DER encoding
    const sequence = Buffer.concat([
      Buffer.from([0x30, 0x44]), // 0x30 (sequence) + length byte (0x44 for 68 bytes)
      Buffer.from([0x02, 0x20]), // 0x02 (integer) + length of r (0x20 = 32 bytes)
      Buffer.from(rHex, 'hex'),
      Buffer.from([0x02, 0x20]), // 0x02 (integer) + length of s (0x20 = 32 bytes)
      Buffer.from(sHex, 'hex')
    ]);

    // Output the DER-encoded signature as a hex string
    console.log(sequence.toString('hex'));

  } catch (error) {
    console.log('Error during signing:', error.message || error);
  }
})();


