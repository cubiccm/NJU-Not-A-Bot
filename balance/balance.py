import requests
import argparse, textwrap
import re, json
import time, sys

sys.path.append(".")
import telegram as tg

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

def getBalance():
  url = "https://wx.nju.edu.cn/njucharge/wap/card/index"
  r = requests.get(url = url, cookies = cookies)
  res = re.findall("balance: \"([-0-9.]+)\"", r.text)

  if len(res):
    print("Card balance:", res[0])
    try:
      return float(res[0])
    except:
      raise Exception("Cannot get card balance")
  else:
    raise Exception("Cannot get card balance")

def getInternetBalance():
  url = "https://wx.nju.edu.cn/njucharge/wap/net/index"
  r = requests.get(url = url, cookies = cookies)
  res = re.findall("netye: \'([-0-9.]+)\'", r.text)
  if len(res):
    print("Internet balance:", res[0])
    try:
      return float(res[0])
    except:
      raise Exception("Cannot get internet balance")
  else:
    raise Exception("Cannot get internet balance")

def convertTime(timestr):
  return "{year}-{month}-{day} {hour}:{minute}:{second}".format(
    year = timestr[0:4],
    month = timestr[4:6],
    day = timestr[6:8],
    hour = timestr[8:10],
    minute = timestr[10:12],
    second = timestr[12:14]
  )

def recharge(target, pwd, amount, original_balance = "Unknown"):
  if target == "card":
    account_type = "campus card"
    url = "https://wx.nju.edu.cn/njucharge/wap/card/recharge"
  elif target == "internet":
    account_type = "Internet account"
    url = "https://wx.nju.edu.cn/njucharge/wap/net/recharge"
  
  params = {
    "fee": recharge_amount,
    "paypwd": args.payment_password,
    "paytype": 1,
    "type": 1
  }
  payment_info = requests.post(url, data = params, cookies = cookies)
  try:
    payment_info = json.loads(payment_info.text)
    payment_id = payment_info["d"]["id"]
  except:
    print("Failed to get payment info")
    try:
      tg.send(textwrap.dedent("""
        <b>❗️Problem on recharging {name}</b>
        Failed to get payment info.
        Original Balance: {balance:.2f} CNY
        Amount: {amount:.2f} CNY
        Time: {time}
        Message: {msg}
      """.format(
        name = account_type,
        balance = original_balance,
        amount = amount,
        time = time.strftime('%Y-%m-%d %H:%M:%S %Z'),
        msg = payment_info["m"],
      )))
    except:
      print("Failed to send telegram message")
    exit()
  
  print("Retrieving payment result")
  if target == "card":
    url = "https://wx.nju.edu.cn/njucharge/wap/card/get-res"
  elif target == "internet":
    url = "https://wx.nju.edu.cn/njucharge/wap/net/get-res"
  params = {"id": payment_id}
  try_count = 0
  bill_status = ""
  while try_count < 10:
    try_count += 1
    time.sleep(0.5)
    payment_result = requests.get(url, params = params, cookies = cookies)
    try:
      payment_result = json.loads(payment_result.text)["d"]
      bill_status = payment_result["billstatus"]
      if bill_status == "2":
        print("{name} recharged successfully".format(name = account_type.capitalize()))
        try:
          if target == "card":
            new_card_balance = getBalance()
          elif target == "internet":
            new_card_balance = getInternetBalance()
          tg.send(textwrap.dedent("""
            <b>✅ {name} recharged successfully</b>
            Original Balance: {orig_balance:.2f} CNY
            New Balance: {balance:.2f} CNY (might subject to a delay)
            Amount: {amount:.2f} CNY
            Method: {method}
            Payee: {payee}
            Type: {bill_name}
            Time: {time} CST
            Message: {msg}
            Transaction ID: {id}
            Reference No.: {refno}
          """.format(
            name = account_type.capitalize(),
            orig_balance = original_balance,
            balance = new_card_balance,
            amount = float(payment_result["amount"]),
            method = payment_result["paidmethod"],
            payee = payment_result["organname"],
            bill_name = payment_result["billname"],
            time = convertTime(payment_result["paytime"]),
            msg = payment_result["retmsg"],
            id = payment_id,
            refno = payment_result["refno"]
          )))
        except:
          print("Failed to send telegram message")
        break
      elif not bill_status == "3" and not bill_status == "1":
        print("Bill status", bill_status)
        try_count += 4
    except:
      try_count += 4
    time.sleep(1)
  if try_count >= 10 and bill_status != "2":
    print("Failed to retrieve payment result, last bill status is", bill_status)
    try:
      tg.send(textwrap.dedent("""
        <b>❗️Problem on recharging {name}</b>
        Unable to retrieve payment result, your card might not be recharged.
        Original Balance: {balance:.2f} CNY
        Amount: {amount:.2f} CNY
        Time: {time}
        Status: {status}
        Message: {msg}
        Transaction ID: {id}
      """.format(
        name = account_type,
        balance = card_balance,
        amount = recharge_amount,
        time = time.strftime('%Y-%m-%d %H:%M:%S %Z'),
        status = bill_status,
        msg = payment_result["retmsg"] or "",
        id = payment_id
      )))
    except:
      print("Failed to send telegram message")

if args.recharge_parameter:
  try:
    arg_params = args.recharge_parameter.split(",", 2)
    args.recharge_threshold = arg_params[0]
    args.recharge_amount = arg_params[1]
    args.payment_password = arg_params[2]
  except:
    print("Invalid recharge parameter")

card_balance = getBalance()
if args.recharge_threshold and args.recharge_amount and args.payment_password:
  try:
    recharge_threshold = float(args.recharge_threshold)
    recharge_amount = float(args.recharge_amount)
  except:
    raise Exception("Invalid recharge parameter")
  if recharge_threshold >= card_balance:
    print("Recharging campus card")
    recharge("card", args.payment_password, recharge_amount, card_balance)
  else:
    print("Card not recharged (balance above threshold)")
else:
  print("Card not recharged (not enough arguments)")

internet_balance = getInternetBalance()
if args.payment_password:
  recharge_threshold = 20.0
  recharge_amount = 10.0
  if recharge_threshold >= internet_balance:
    print("Recharging Internet account")
    recharge("internet", args.payment_password, recharge_amount, internet_balance)
  else:
    print("Internet account not recharged (balance above threshold)")
else:
  print("Internet account not recharged (not enough arguments)")