from captcha.image import ImageCaptcha
import random
import string
import base64


def generate_captcha():
    # 生成随机验证码
    letters = string.ascii_letters
    captcha_text = ''.join(random.choice(letters) for i in range(4))
    # 创建图片验证码
    image = ImageCaptcha(width=90, height=50)
    captcha_image = image.generate(captcha_text)
    # 将验证码图片以二进制形式写入内存
    captcha_binary = base64.b64encode(captcha_image.getvalue()).decode('utf-8')
    return captcha_text, captcha_binary
