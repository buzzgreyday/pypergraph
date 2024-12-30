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

  // Convert the SHA512 hash (hex string) into a Buffer
  const sha512Hash = Buffer.from(txHash, 'hex');

  try {
    // Sign the SHA512 hash using the private key
    const sig = await secp.signAsync(sha512Hash, privateKey, {lowS: true});
    const { r, s } = sig;

    const encodeInteger = (integer) => {
      let hex = integer.toString(16); // Convert to hex string
      if (hex.length % 2 !== 0) {
        hex = '0' + hex; // Ensure even-length hex
      }
      if (hex.startsWith('8') || hex.startsWith('9') || hex.startsWith('a') || hex.startsWith('b') ||
          hex.startsWith('c') || hex.startsWith('d') || hex.startsWith('e') || hex.startsWith('f')) {
        hex = '00' + hex; // Add leading zero to avoid negative interpretation
      }
      return Buffer.concat([Buffer.from([0x02, hex.length / 2]), Buffer.from(hex, 'hex')]);
    };

    const encodedR = encodeInteger(r);
    const encodedS = encodeInteger(s);

    // Calculate total sequence length
    const totalLength = encodedR.length + encodedS.length;
    const sequence = Buffer.concat([
      Buffer.from([0x30, totalLength]), // Sequence tag + total length
      encodedR,
      encodedS
    ]);

    console.log(sequence.toString('hex'));
  } catch (error) {
    console.log('Error during signing:', error.message || error);
  }
})();
