import pytest
from pypergraph.dag_keystore import KeyStore
from pypergraph.dag_network import DagTokenNetwork
from secrets import mnemo

@pytest.mark.asyncio
async def test_sign_data():
    keystore = KeyStore()
    pk = keystore.get_private_key_from_mnemonic(phrase=mnemo)
    # Build the signature request
    signature_request = {
        "field1": "content_field_1",
        "field2": {
            "field2_1": True,
            "field2_2": 12332435,
            "field2_3": {
                "field2_3_1": "content_field2_3_1",
            },
        },
        "field3": [1, 2, 3, 4],
        "field4": None,
    }

    signature, hash_ = keystore.data_sign(pk, signature_request)
    print(signature, hash_)
    pub_k = keystore.get_public_key_from_private(pk)
    assert keystore.verify(pub_k, hash_, signature) is True, "Data sign failed, couldn't verify signature"