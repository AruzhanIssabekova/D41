from django.core.signing import Signer

def sign_data(data):
    signer = Signer()
    return signer.sign(data)

def unsign_data(signed_data):
    signer = Signer()
    return signer.unsign(signed_data)
