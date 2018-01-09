from qiniu import *


class Qiniuyun():
    def __init__(self, ak, sk, bucket_name):
        self.bucket_name = bucket_name
        self.bucket = BucketManager(Auth(ak, sk))

    def fetch(self, url, name):
        self.bucket.fetch(url, self.bucket_name, name)
