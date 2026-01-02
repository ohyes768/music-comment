"""
网易云音乐API加密模块

实现评论接口所需的 AES + RSA 加密算法
"""

import json
import base64
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
from Crypto.Random import get_random_bytes


class NeteaseCrypto:
    """网易云音乐加密工具类

    实现评论接口所需的加密算法
    """

    # 固定参数（逆向分析得出）
    RSA_PUB_KEY = "010001"
    RSA_MODULUS = "00e0b509f6259df8642dbc35662901477df22677ec152b5ff68ace615bb7b725152b3ab17a876aea8a5aa76d2e417629ec4ee341f56135fccf695280104e0312ecbda92557c93870114af6c9d05c4f7f0c3685b7a46bee255932575cce10b424d813cfe4875d3e82047b97ddef52741d546b8e289dc6935b3ece0462db0a22b8e7"
    AES_KEY = "0CoJUm6Qyw8W8jud"
    AES_IV = "0102030405060708"

    # 固定16位随机字符串（让 encSecKey 固定）
    FIXED_RANDOM = "4BfsFyBWTSe0C5eQ"

    # 对应的固定 encSecKey
    FIXED_ENC_SEC_KEY = "ac120b775a368f6cdf196f173ac16bccaa08e8589fdd824f7445cb71a6f12f7a25da019240ce2f69a214ef34ba2795b057b1cf4fd24fbf4bd9f78167c9c69de4ee8be3bb8bb9119e2a0328219497864558363bc8e5c8a7999822f127dc0d7fc3bbf0a53f3e2e091eba811eb57558dd6290ab4224f636cea2d264bb2ed7c7cee8"

    @staticmethod
    def aes_encrypt(text: str, key: str, iv: str) -> str:
        """AES-CBC 加密

        Args:
            text: 待加密文本
            key: AES密钥
            iv: 初始化向量

        Returns:
            str: Base64编码的密文
        """
        cipher = AES.new(
            key.encode('utf-8'),
            AES.MODE_CBC,
            iv.encode('utf-8')
        )
        padded_text = pad(text.encode('utf-8'), AES.block_size)
        ciphertext = cipher.encrypt(padded_text)
        return base64.b64encode(ciphertext).decode('utf-8')

    @classmethod
    def encrypt_request(cls, request_data: dict) -> dict:
        """加密请求数据

        Args:
            request_data: 请求数据字典

        Returns:
            dict: 包含 params 和 encSecKey 的加密数据
        """
        # 转换为 JSON 字符串
        text = json.dumps(request_data)

        # 第一次 AES 加密（使用固定密钥）
        enc_text1 = cls.aes_encrypt(text, cls.AES_KEY, cls.AES_IV)

        # 第二次 AES 加密（使用随机字符串）
        enc_text2 = cls.aes_encrypt(enc_text1, cls.FIXED_RANDOM, cls.AES_IV)

        return {
            'params': enc_text2,
            'encSecKey': cls.FIXED_ENC_SEC_KEY
        }
