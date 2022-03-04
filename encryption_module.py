import rsa
import hashlib
import pathlib
from cryptography.fernet import Fernet


def generate_PKI_keys(key_length, purpose):
    print('generating keys for ' + purpose)
    (pub_key, pri_key) = rsa.newkeys(key_length)
    string_pub_key = pub_key.save_pkcs1('PEM')
    string_pri_key = pri_key.save_pkcs1('PEM')
    with open('temporary/' + purpose + "_" + 'private' + ".key", 'wb') as f1:
        f1.write(string_pri_key)
    with open('temporary/' + purpose + "_" + 'public' + ".key", 'wb') as f2:
        f2.write(string_pub_key)
    return string_pri_key, string_pub_key


# def generate_schema_keys(purpose):
#     (pub_key, pri_key) = rsa.newkeys(2048)
#     string_pub_key = pub_key.save_pkcs1('PEM')
#     string_pri_key = pri_key.save_pkcs1('PEM')
#     with open('local_files/keys/' + purpose + "_" + terminology.private + ".key", 'wb') as f1:
#         f1.write(string_pri_key)
#     with open('local_files/keys/' + purpose + "_" + terminology.public + ".key", 'wb') as f2:
#         f2.write(string_pub_key)
#     return string_pri_key, string_pub_key


def generate_symmetric_key():
    symmetric_key = Fernet.generate_key()
    # print('A new symmetric key is generated')
    return symmetric_key


def retrieve_key_from_saved_file(label, private_or_public):
    path = 'temporary/' + label + "_key_" + private_or_public + ".key"
    file_path = pathlib.Path(path)
    with open(file_path, 'rb') as f:
        if private_or_public == 'private':
            return rsa.PrivateKey.load_pkcs1(f.read())
        if private_or_public == 'public':
            return rsa.PublicKey.load_pkcs1(f.read())
        return None


def retrieve_signature_from_saved_key(object_used_for_signature, label_of_saved_key):
    key = prepare_key_for_use('private', label_of_saved_key, None)
    signature = produce_serialized_signature(object_used_for_signature, key)
    return deserialize_signature(signature)


def prepare_key_for_use(private_or_public, label_of_saved_key=None, actual_key=None):
    if label_of_saved_key:
        return retrieve_key_from_saved_file(label_of_saved_key, private_or_public)
    if actual_key:
        bytes_key = actual_key.encode('latin-1')
        if private_or_public == 'private':
            return rsa.PrivateKey.load_pkcs1(bytes_key, format='PEM')
        if private_or_public == 'public':
            return rsa.key.PublicKey.load_pkcs1(bytes_key, format='PEM')
            # or..(but not secure):
            # return pickle.loads(bytes_key)


def encrypt_PKI(plain_text, pub_key):
    encoded_msg = plain_text.encode('utf-8')
    encrypted_msg = rsa.encrypt(encoded_msg, pub_key)
    return encrypted_msg


def encrypt_symmetric(object_to_be_encrypted, symmetric_key):
    cipher = Fernet(symmetric_key)
    encrypted_object = cipher.encrypt(object_to_be_encrypted)
    # print('Object is encrypted using symmetric key')
    return encrypted_object


def decrypt_PKI(encrypted_msg, pri_key):
    ready = encrypted_msg.encode('latin-1')
    msg = rsa.decrypt(ready, pri_key)
    ready_symmetric_key = Fernet(msg)
    return ready_symmetric_key


def decrypt_symmetric(encrypted_object, key):
    encoded_encrypted_object = encrypted_object.encode('latin-1')
    encoded_object = key.decrypt(encoded_encrypted_object)
    return encoded_object.decode('latin-1')


def produce_serialized_signature(object_to_be_used_for_signature, serialized_key):
    hashed_object = hashing_function(object_to_be_used_for_signature)
    encoded_hashed_object = hashed_object.encode('UTF-8')
    return rsa.sign(encoded_hashed_object, serialized_key, 'SHA-256')


def serialize_signature(deserialized_signature):
    return deserialized_signature.encode('latin-1')


def deserialize_signature(serialized_signature):
    return serialized_signature.decode('latin-1')


def serialize_key(old_key, public_or_private):
    bytes_key = old_key.encode('UTF-8')
    if public_or_private == terminology.public:
        return rsa.key.PublicKey.load_pkcs1(bytes_key, format='PEM')
    if public_or_private == terminology.private:
        return rsa.key.PrivateKey.load_pkcs1(bytes_key, format='PEM')


def deserialize_key(serialized_key):
    bytes_key = serialized_key.save_pkcs1('PEM')
    return bytes_key.decode('UTF-8')


def hashing_function(entity):
    h = hashlib.sha256()
    h.update(str(entity).encode(encoding='UTF-8'))
    return h.hexdigest()


def verify_credential(hashed_credential, signature, key):
    encoded_hashed_credential = hashed_credential.encode('UTF-8')
    encoded_signature = signature.encode('latin-1')
    return verify(encoded_hashed_credential, encoded_signature, key)


def verify_signature(hashed_object, deserialized_signature, key):
    encoded_hashed_credential = hashed_object.encode('UTF-8')
    serialized_signature = serialize_signature(deserialized_signature)
    return verify(encoded_hashed_credential, serialized_signature, key)


def verify(hashed_credential, signature, pub_key):
    valid = False
    try:
        rsa.verify(hashed_credential, signature, pub_key)
        valid = True
    except Exception as e:
        print('a signature is found invalid!')
        print(e)
    return valid
