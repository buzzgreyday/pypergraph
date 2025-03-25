from bip32utils import BIP32Key


class Bip32Helper:
    @staticmethod
    def get_root_key_from_seed(seed_bytes) -> BIP32Key:
        """
        Derive the HD root/master key from a seed entropy in bytes format.

        :param seed_bytes: The seed entropy in bytes format.
        :return: The root/master key.
        """
        return BIP32Key.fromEntropy(seed_bytes)


    def get_hd_root_key_from_seed(self, seed_bytes: bytes, hd_path: str) -> BIP32Key:
        """
        Derive the private key from a seed entropy using derived path.

        :param seed_bytes: The seed in bytes format.
        :param hd_path: The derivation path.
        :return: The private key as a hexadecimal string.
        """
        path_parts = [int(part.strip("'")) for part in hd_path.split("/")[1:]]
        purpose = path_parts[0] + 2 ** 31
        coin_type = path_parts[1] + 2 ** 31
        account = path_parts[2] + 2 ** 31
        change = 0
        index = path_parts[3]
        root_key = self.get_root_key_from_seed(seed_bytes=seed_bytes)
        return root_key.ChildKey(purpose).ChildKey(coin_type).ChildKey(account).ChildKey(change).ChildKey(
            index)
