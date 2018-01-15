from qiniu import *
from datetime import *

qiniu_ak = '765Mhr-G-dZcwt07C50ki-7eFfptNFvESXd0OjtW'
qiniu_sk = '_maWBwZBsSlaFFsaDANX11EWwAzUrGG1cbHYUNkw'
class Qiniuyun():
    def __init__(self, ak, sk, bucket_name):
        self.bucket_name = bucket_name
        self.bucket = BucketManager(Auth(ak, sk))

    def fetch(self, url, name):
        self.bucket.fetch(url, self.bucket_name, name)

    def stat(self, names):
        data = {}
        ops = build_batch_stat(self.bucket_name, names)
        ret, info = self.bucket.batch(ops)
        n = 0
        for info in eval(info.text_body):
            if info['code'] == 200:
                data[names[n]] = str(datetime.fromtimestamp(info['data']['putTime'] // 10 ** 7))
            else:
                data[names[n]] = None
            n += 1
        return data

    def delete(self, names):
        ops = build_batch_delete(self.bucket_name, names)
        self.bucket.batch(ops)
