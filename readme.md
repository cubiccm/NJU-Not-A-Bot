# NJU - I'm Not A Robot

南京大学“i南大”信息门户自动化工具，基于 GitHub Actions。

目前支持收集宿舍用电情况并绘制图表。

## 用法

### 环境

需要安装 Python 3 并通过

``` shell
pip install -r requirements.txt
```

安装必要的依赖环境。

### 记录电量

``` shell
python electricity/elec-monitor.py --room=[[area-id]],[[build_id]],[[room-id]] --key=[[eai-sess]]
```

其中，`area-id`、`build_id`、`room_id` 可以在缴费页链接中提取，`eai-sess` 可以在 [i南大信息门户](https://wx.nju.edu.cn/homepage/wap/default/home) 网页的 Cookies 中找到。

例如，`area-id` 为 `02`（仙林校区），`build_id` 为 `xl01`，`room_id` 为 `A101`，则该参数为 `--room=02,xl01,A101`。

电量成功获取后会记录到 `data.csv` 中。

### 展示电量

```shell
python electricity/elec-graph.py
```

### GitHub Actions

借助 GitHub Actions 可以自动化记录电量，并通过 Pull Request 更新至 electricity/data.csv。设置的运行频率为每十分钟一次，但实际运行频率可能会更低；亦可在 Action 界面手动执行。

需要先在 Repo 设置中添加两个 Secrets：`ELEC_ROOM` 和 `EAISESS`，分别对应两个输入参数。如 `ELEC_ROOM` 为 `02,xl06,1014`，`EAISESS` 为 `gks2bdj093zfidj91cidkofkw6`。

## TO-DO
- [ ] 使用账号和密码自动登录信息门户
- [ ] 自动充值（校园卡/电费/网费）
- [ ] 图书自动续借
- [ ] 基于 Telegram / 邮件 的消息提醒
  - [ ] 低余额 / 充值成功信息
  - [ ] 体育打卡数量提醒