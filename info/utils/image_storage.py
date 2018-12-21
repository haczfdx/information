from qiniu import Auth, put_data

access_key = "jF8a687N_FVbBLBOpPQDvG9RcEjLwad9NeH5lXi5"
secret_key = "99_SMvSr_VQY1zW1gWd4zimbjszP2HiXjd3Qbj7V"
bucket_name = 'mytestqiniu'


def storage(data):
    try:
        q = Auth(access_key, secret_key)
        token = q.upload_token(bucket_name)
        ret, info = put_data(token, None, data)
        print(ret, info)
    except Exception as e:
        raise e

    if info.status_code != 200:
        raise Exception("上传图片失败")
    return ret["key"]


if __name__ == '__main__':
    file = input('请输入文件路径')
    with open(file, 'rb') as f:
        storage(f.read())
