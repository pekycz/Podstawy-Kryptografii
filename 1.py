import hashlib
import os

def hash(to_hash,method):
    return hashlib.new(method, to_hash.encode()).hexdigest()

