import * as secp from '@noble/secp256k1';
import * as jsSha512 from 'js-sha512';
import { hmac } from '@noble/hashes/hmac';
import { sha256 } from '@noble/hashes/sha256';

(async () => {
  // Set the async HMAC function
  secp.etc.hmacSha256Async = async (key, ...messages) =>
    hmac.create(sha256, key).update(secp.etc.concatBytes(...messages)).digest();

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
    const sig = await secp.signAsync(sha512Hash, privateKey, {lowS: true});
const { r, s } = sig;

    const encodeInteger = (integer) => {
      let hex = integer.toString(16).padStart(64, '0'); // Ensure 32 bytes
      if (hex.startsWith('8') || hex.length % 2 !== 0) {
        hex = '00' + hex; // Add leading zero for positive interpretation
      }
      return Buffer.concat([Buffer.from([0x02, hex.length / 2]), Buffer.from(hex, 'hex')]);
    };

    const encodedR = encodeInteger(r);
    const encodedS = encodeInteger(s);

    const sequence = Buffer.concat([
      Buffer.from([0x30, encodedR.length + encodedS.length]), // Sequence + total length
      encodedR,
      encodedS
    ]);

    console.log(sequence.toString('hex'));
  } catch (error) {
    console.log('Error during signing:', error.message || error);
  }
})();
