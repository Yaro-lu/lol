# 双色球 / 大乐透查询

按期号和输入号码对照双色球、大乐透开奖结果，显示匹配号码与中奖查询结果。

## 运行

需要 Python 3、Tkinter、requests、Beautiful Soup 4，以及网络连接。在仓库根目录执行：

```bash
python -m pip install -r tools/lottery-checker/requirements.txt
python tools/lottery-checker/main.py
```

## 使用

1. 选择“大乐透查询”或“双色球查询”。
2. 等待最近期号读取完成，选择需要查询的期号。
3. 输入对应的前后区或红蓝球号码，用空格分隔。
4. 点击“查询”，查看结果。

程序从 `kaijiang.78500.cn` 的第三方开奖页面读取数据，当前缓存最近 20 期；联网读取与页面解析是否成功取决于该站点的响应和结构。

[返回工具合集](../../README.md)
