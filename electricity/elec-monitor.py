import requests
import argparse
import time, datetime
import re
import csv

parser = argparse.ArgumentParser()
parser.add_argument("-r", "--room", help = "Specify room in format \"area_id,build_id,room_id\"")
parser.add_argument("-k", "--key", help = "eai-sess cookies value")
args = parser.parse_args()

if args.room:
  try:
    room = args.room.split(",")
    url_params = {
      "area_id": room[0],
      "build_id": room[1],
      "room_id": room[2]
    }
  except:
    raise Exception("Cannot parse room argument")
else:
  raise Exception("Room argument required")

if args.key:
  cookies = {
    "eai-sess": args.key
  }
else:
  raise Exception("Key required (eai-sess value)")

url = "https://wx.nju.edu.cn/njucharge/wap/electric/charge"
r = requests.get(url = url, params = url_params, cookies = cookies)
res = re.findall("dianyue:\"([-0-9.]+)\"", r.text)
if len(res):
  print(res[0])
  with open("electricity/data.csv", "a") as f:
    csv.writer(f).writerow([datetime.datetime.now(), res[0]])
else:
  raise Exception("Cannot fetch electricity data")