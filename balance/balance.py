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

def convertTime(timestr):
  return "{year}-{month}-{day} {hour}:{minute}:{second}".format(
    year = timestr[0:4],
    month = timestr[4:6],
    day = timestr[6:8],
    hour = timestr[8:10],
    minute = timestr[10:12],
    second = timestr[12:14]
  )

card_balance = getBalance()

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
      print("Failed to get payment info")
      try:
        tg.send(textwrap.dedent("""
          <b>❗️Problem on recharging campus card</b>
          Failed to get payment info.
          Original Balance: {balance:.2f} CNY
          Amount: {amount:.2f} CNY
          Time: {time}
          Message: {msg}
        """.format(
          balance = card_balance,
          amount = recharge_amount,
          time = time.strftime('%Y-%m-%d %H:%M:%S %Z'),
          msg = payment_info["m"],
        )))
      except:
        print("Failed to send telegram message")
      exit()

    print("Retrieving payment result")
    url = "https://wx.nju.edu.cn/njucharge/wap/card/get-res"
    params = {"id": payment_id}
    try_count = 0
    while try_count < 10:
      try_count += 1
      payment_result = requests.get(url, params = params, cookies = cookies)
      try:
        payment_result = json.loads(payment_result.text)["d"]
        bill_status = payment_result["billstatus"]
        if bill_status == "2":
          print("Recharged successfully")
          try:
            new_card_balance = getBalance()
            tg.send(textwrap.dedent("""
              <b>✅Campus card recharged successfully</b>
              New Balance: {balance:.2f} CNY
              Amount: {amount:.2f} CNY
              Method: {method}
              Time: {time} CST
              Message: {msg}
              Transaction ID: {id}
              Reference No.: {refno}
            """.format(
              balance = new_card_balance,
              amount = float(payment_result["amount"]),
              method = payment_result["paidmethod"],
              time = convertTime(payment_result["paytime"]),
              msg = payment_result["retmsg"],
              id = payment_id,
              refno = payment_result["refno"]
            )))
          except:
            print("Failed to send telegram message")
          break
        elif not bill_status == "3":
          print("Bill status", bill_status)
          try_count += 6
      except:
        try_count += 6
      time.sleep(1)
    if try_count >= 10 and bill_status != "2":
      print("Failed to retrieve payment result, last bill status is", bill_status)
      try:
        tg.send(textwrap.dedent("""
          <b>❗️Problem on recharging campus card</b>
          Unable to retrieve payment result, your card might not be recharged.
          Original Balance: {balance:.2f} CNY
          Amount: {amount:.2f} CNY
          Time: {time}
          Status: {status}
          Message: {msg}
          Transaction ID: {id}
        """.format(
          balance = card_balance,
          amount = recharge_amount,
          time = time.strftime('%Y-%m-%d %H:%M:%S %Z'),
          status = bill_status,
          msg = payment_result["retmsg"] or "",
          id = payment_id
        )))
      except:
        print("Failed to send telegram message")
  else:
    print("Card not recharged (card balance above threshold)")
else:
  print("Card not recharged (not enough arguments)")