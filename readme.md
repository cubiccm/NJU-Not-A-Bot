# NJU - I'm Not A Robot

南京大学“i南大”信息门户自动化工具，基于 GitHub Actions。

目前支持校园卡余额查询及充值，以及收集宿舍用电情况并绘制图表。

## 借助 GitHub Actions 实现自动化

借助 GitHub Actions 可以为校园卡自动充值、自动化记录电量并更新至 `electricity/data.csv`。设置的运行频率为每十分钟一次，但实际运行频率可能会更低；亦可在 Action 界面手动执行。

在执行 Actions 前需要先在 Repo 设定中设置执行参数。在 Repo 的 `Settings -> Secrets` 中添加 Repository Secrets，并按下方说明设置名称和值即可。

### EAI-SESS 参数

几乎所有操作都需要设定 `EAISESS`，未设定该项时 GitHub Actions 将会执行失败。这一参数可以在 [i南大信息门户](https://wx.nju.edu.cn/homepage/wap/default/home) 网页的 Cookies 中找到，如 `gks2bdj093zfidj91cidkofkw6`。

### 校园卡充值

如需校园卡自动充值，还需要设定 `CARD_RECHARGE` 充值参数为 `[[recharge-threshold]],[[recharge-amount]],[[payment-password]]`。

其中，`recharge-threshold` 为最小充值阈值，即当校园卡余额小于等于这个阈值时，才会执行充值操作。`recharge-amount` 为充值金额，由于信息门户限制，可能只能充值整数金额。`payment-password` 为在线支付密码，即信息门户充值操作所需要的密码。充值操作会从信息门户绑定银行卡中扣除金额。这三个参数以逗号分隔。

例如，`50,50,pasSwoddd` 代表校园卡余额不高于 50CNY 时，会自动充值 50CNY 到卡内，最后一项为在线支付密码。

*如果在线支付密码中含有 `,`，不需要进行转义，直接输入即可。如果不指定任何充值信息，将仅查询校园卡余额。*

### 记录房间电量

如需使用电量查询及自动记录，还需要设定 `ELEC_ROOM` 房间参数为 `[[area-id]],[[build-id]],[[room-id]]`。

其中，`area-id`、`build-id`、`room_id` 可以在缴费页链接中提取，分别代表校区（鼓楼：`01`，仙林：`02`）、楼栋（如 `gl01` / `xl01`）及房间号（如 `101` / `A301` / `3081`）。

例如，`area-id` 为 `02`（仙林校区），`build-id` 为 `xl01`，`room_id` 为 `A101`，则该参数为 `02,xl01,A101`。

电量成功获取后会记录到 `data.csv` 中。

### 连接 Telegram

需要设置 `TG_BOT_TOKEN` 和 `TG_CHAT_ID` 两项参数。连接 Telegram 后，将可自动发消息到指定的 Telegram 账号。

要在 Telegram 接收信息，需要拥有 Telegram 账号并在 [BotFather](https://t.me/botfather) 处注册一个 [Bot](https://core.telegram.org/bots)。这个机器人将用于向 Telegram 账号发送信息。之后，将获得的 Bot token 填入 Repo 参数 `TG_BOT_TOKEN`，并将你的（需要接收消息的）账号ID填入 `TG_CHAT_ID`。

注意，账号ID不是注册用户名或注册手机号，而是一个唯一数字ID。可以和 [Chat ID Echo](https://t.me/chatid_echo_bot) 对话或和自己的机器人对话以获取这个ID。

## 本地执行用法

### 环境

需要安装 Python 3 并在终端执行

``` shell
pip install -r requirements.txt
```

以安装必要的依赖环境。

### EAI-SESS 参数

几乎所有需要访问账号信息的操作都需要指定 `eai-sess` 参数。这一参数可以在 [i南大信息门户](https://wx.nju.edu.cn/homepage/wap/default/home) 网页的 Cookies 中找到。

### 校园卡充值

``` shell
python balance/balance.py --recharge-parameter=[[recharge-threshold]],[[recharge-amount]],[[payment-password]] --key=[[eai-sess]]
```
例如，`--recharge-parameter=50,50,pasSwoddd` 代表校园卡余额不高于 50CNY 时，会自动充值 50CNY 到卡内，最后一项为在线支付密码。

### 记录房间电量

``` shell
python electricity/elec-monitor.py --room=[[area-id]],[[build-id]],[[room-id]] --key=[[eai-sess]]
```

例如 `--room=02,xl01,A101`。电量成功获取后会记录到 `data.csv` 中。

### 展示房间电量

```shell
python electricity/elec-graph.py
```

### 连接 Telegram
设置环境变量：`_TG_BOT_TOKEN` 及 `_TG_CHAT_ID` 即可自动发消息至 Telegram。

## TO-DO
- [ ] 使用账号和密码自动登录信息门户
- [ ] 自动充值
  - [x] 校园卡
  - [ ] 电费
  - [ ] 网费
- [ ] 图书自动续借
- [ ] 基于 Telegram / 邮件 的消息提醒
  - [x] 充值成功信息
  - [ ] 费用低提醒
  - [ ] 体育打卡数量提醒