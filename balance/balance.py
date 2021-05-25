import requests
import argparse
import re, json
import time

parser = argparse.ArgumentParser()
parser.add_argument("-k", "--key", help = "eai-sess cookies value")
parser.add_argument("-t", "--recharge-threshold", help = "Card will be automatically recharged when balance reached this threshold or less")
parser.add_argument("-a", "--recharge-amount", help = "Amount to charge automatically")
parser.add_argument("-p", "--payment-password", help = "Campus card online payment password")
parser.add_argument("-r", "--recharge-parameter", help = "A compilation of --recharge-threshold, --recharge-amount and --payment-password in the format of \"threshold,amount,password\"")
args = parser.parse_args()

if args.key:
  cookies = {
    "eai-sess": args.key
  }
else:
  raise Exception("Key required (eai-sess value)")

url = "https://wx.nju.edu.cn/njucharge/wap/card/index"
r = requests.get(url = url, cookies = cookies)
res = re.findall("balance: \"([-0-9.]+)\"", r.text)

if len(res):
  print("Card balance:", res[0])
  try:
    card_balance = float(res[0])
  except:
    raise Exception("Cannot get card balance")
else:
  raise Exception("Cannot get card balance")

if args.recharge_parameter:
  try:
    arg_params = args.recharge_parameter.split(",", 2)
    args.recharge_threshold = arg_params[0]
    args.recharge_amount = arg_params[1]
    args.payment_password = arg_params[2]
  except:
    print("Invalid recharge parameter")

if args.recharge_threshold and args.recharge_amount and args.payment_password:
  try:
    recharge_threshold = float(args.recharge_threshold)
    recharge_amount = float(args.recharge_amount)
  except:
    raise Exception("Invalid recharge parameter")
  if recharge_threshold >= card_balance:
    print("Recharging")
    url = "https://wx.nju.edu.cn/njucharge/wap/card/recharge"
    params = {
      "fee": recharge_amount,
      "paypwd": args.payment_password,
      "paytype": 1
    }
    payment_info = requests.post(url, data = params, cookies = cookies)
    try:
      payment_info = json.loads(payment_info.text)
      payment_id = payment_info["d"]["id"]
    except:
      raise Exception("Failed to get payment info")
    print("Retrieving payment result")
    url = "https://wx.nju.edu.cn/njucharge/wap/card/get-res"
    params = {"id": payment_id}
    try_count = 0
    while try_count < 10:
      try_count += 1
      payment_result = requests.get(url, params = params, cookies = cookies)
      try:
        payment_result = json.loads(payment_result.text)
        bill_status = payment_result["d"]["billstatus"]
        if bill_status == "2":
          print("Recharged successfully")
          break
        elif not bill_status == "3":
          print("Bill status", bill_status)
          try_count += 6
      except:
        try_count += 6
      time.sleep(1)
    if try_count >= 10:
      print("Unable to retrieve payment result, last bill status is", bill_status)
  else:
    print("Card not recharged (card balance above threshold)")
else:
  print("Card not recharged (not enough arguments)")