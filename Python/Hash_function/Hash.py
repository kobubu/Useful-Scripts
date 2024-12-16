import hashlib

def get_hash(experiment_name, user_id):
    user_str = f'{user_id}{experiment_name}'
    user_str = user_str.encode('utf-8')
    hashed = hashlib.sha256(user_str).hexdigest()[-15:]
    return int(hashed, 16)

experiment_name = 'ab_testing'
user_id = 253_482
n_buckets = 100

user_hashed = get_hash(experiment_name, user_id)
user_bucket_id = user_hashed % n_buckets

print(user_id)
