from typing import Dict


class KeyTrio:
    def __init__(self, private_key: str, public_key: str, address: str):
        """

        :param private_key: Private key in hex format.
        :param public_key: Public key key in hex format.
        :param address: DAG address.
        """
        self.private_key = private_key
        self.public_key = public_key
        self.address = address

    def to_dict(self) -> Dict:
        """
        Transform KeyTrio object to dictionary.
        :return: Dictionary.
        """
        return {"private_key": self.private_key, "public_key": self.public_key, "address": self.address}