import requests
from bs4 import BeautifulSoup
import json, datetime
import sys, os

import random
import base64
from Crypto.Cipher import AES
from Crypto.Util import Padding

import argparse

parser = argparse.ArgumentParser()
parser.add_argument("-c", "--cookie", help = "eai-sess cookies value")
parser.add_argument("-u", "--uid", help = "NJU Account ID")
parser.add_argument("-p", "--pwd", help = "NJU Account Password")
parser.add_argument("--github", action='store_true')
args = parser.parse_args()

if args.cookie == "" and args.uid == "":
  raise Exception("A NJU ID or an EAI-SESS cookie should be provided to login.")

if args.cookie and args.cookie != "":
  print("::set-output name=logincookie::{cookie}".format(cookie = args.cookie))
else:
  username = args.uid
  password = args.pwd
  captcha_fill = not args.github

  access_url = "https://wx.nju.edu.cn/homepage/wap/default/home"
  login_url = "https://authserver.nju.edu.cn/authserver/login?service=https%3A%2F%2Fwx.nju.edu.cn%2Fa_nju%2Fapi%2Fsso%2Findex%3Fredirect%3Dhttps%253A%252F%252Fwx.nju.edu.cn%252Fhomepage%252Fwap%252Fdefault%252Fhome%26from%3Dwap"

  # Reference: https://github.com/forewing/nju-health-checkin/blob/master/checkin.py
  def encryptAES(data, key):
    def rds(len):
      return ''.join(random.choices("ABCDEFGHJKMNPQRSTWXYZabcdefhijkmnprstwxyz2345678", k=len))
    encrypt = AES.new(key.strip().encode('utf-8'), AES.MODE_CBC, rds(16).encode('utf-8'))
    return base64.b64encode(encrypt.encrypt(Padding.pad((rds(64) + data).encode('utf-8'), 16))).decode('utf-8')

  def getInput(soup, id=None, name=None):
    if id:
      return soup.find("input", {"id": id})['value']
    elif name:
      return soup.find("input", {"name": name})['value']

  s = requests.Session()
  r = s.get(access_url)
  try:
    soup = BeautifulSoup(r.text, 'html.parser')
    data = {
      'username': username,
      'password': encryptAES(password, getInput(soup, id="pwdDefaultEncryptSalt")),
      'lt': getInput(soup, name="lt"),
      'dllt': "userNamePasswordLogin",
      'execution': getInput(soup, name="execution"),
      '_eventId': getInput(soup, name="_eventId"),
      'rmShown': getInput(soup, name="rmShown"),
    }
  except:
    print("Failed to retrieve login information")

  r = requests.get("https://authserver.nju.edu.cn/authserver/needCaptcha.html?username=" + username)
  if r.text == "true":
    if captcha_fill == False:
      raise Exception("CAPTCHA required.")
    # os.system("pip install -r foundation/muggle_ocr/requirements.txt")
    print("CAPTCHA required, initializing OCR...")
    import muggle_ocr
    os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
    
    print("Obtaining CAPTCHA...")
    res = s.get("https://authserver.nju.edu.cn/authserver/captcha.html")
    
    print("Solving CAPTCHA...")
    sdk = muggle_ocr.SDK(model_type = muggle_ocr.ModelType.Captcha)
    captcha_text = sdk.predict(image_bytes = res.content)
    print("CAPTCHA:", captcha_text)
    
    data["captchaResponse"] = captcha_text

  r = s.post(login_url, data)
  if r.url != access_url:
    raise Exception("Failed to login")

  if "eai-sess" in s.cookies:
    if args.github:
      print("::set-output name=logincookie::{cookie}".format(cookie = s.cookies["eai-sess"]))
    else:
      print(s.cookies["eai-sess"])
      os.environ["NJU_EAISESS"] = s.cookies["eai-sess"]
  else:
    raise Exception("Unable to get EAI_SESS")