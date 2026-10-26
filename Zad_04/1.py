import hashlib

def hash(to_hash,method):
    return hashlib.new(method, to_hash.encode()).hexdigest()
