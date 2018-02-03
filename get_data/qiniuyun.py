from datetime import *

from qiniu import *

from key import *


class Qiniuyun():
    def __init__(self, ak, sk, bucket_name):
        self.bucket_name = bucket_name
        self.bucket = BucketManager(Auth(ak, sk))

    def fetch(self, url, name):
        self.bucket.fetch(url, self.bucket_name, name)

    def stat(self, names):
        ops = build_batch_stat(self.bucket_name, names)
        ret, info = self.bucket.batch(ops)
        print(info)
        data = {}
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


if __name__ == '__main__':
    bucket_name = 'rail'
    qiniuyun = Qiniuyun(qiniu_ak, qiniu_sk, bucket_name)
    print(qiniuyun.delete(['station_img/万州.jpg']))
