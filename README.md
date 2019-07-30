

# 腾讯弹幕抓取器

首先我们来看一下它是怎么工作的吧.

![useage.gif](.//media/useage.gif)


## Feature

- 异步任务抓取
- 任意视频弹幕抓取
- 可定制单集时长
- XLSX生成
- 词云生成
- json生成

## 环境安装

我们通过如下命令克隆代码仓库到本地并通过pip安装依赖包

```
git clone git@github.com:aoii103/Tencent_danmu.git
cd Tencent_danmu
pip install -r requirements.txt
```


## 基础运行

```
python main.py -u [url]
```

## 命令参数

```
Usage: main.py [OPTIONS]

Options:
  -u, --url TEXT               指定目标URL
  -t, --max_time INTEGER       指定每集时间长度，不宜过大(针对vip视频)
  -v, --vip                    vip默认设置15000秒
  -c, --cons INTEGER           爬行并发数量
  -n, --new                    不使用缓存生成
  -e, --excel                  是否生成Excel
  -w, --words                  是否生成词云
  -f, --use_frequencies        是否使用词频
  -b, --words_background TEXT  指定词云背景图
  -d, --is_dark                是否为纯黑底色
  -g, --graph                  是否生成分析图
  --help                       Show this message and exit.
```

## 案例

1. 指定鹦鹉图片作为背景生成《流浪地球》词云,纯黑底色。
    ```
    python3 main.py -u https://v.qq.com/x/cover/3fvg46217gw800n/h0030qj4fov.html -wdv  -b ~/Desktop/pr.jpg
    ```

    ![lldq.png](.//media/lldq.png)

2. 以海报为颜色模板生成《亲爱的，热爱的》词云，纯黑底色。并导出excel。
```
python3 main.py -u https://v.qq.com/x/cover/xbd1y6fvwl3maoz/t00313mumzy.html -wefd
```

- 词云

![lldq.png](.//media/qad.png)

- 弹幕excel 

    - `upcount` 点赞数
    - `commentid` 弹幕ID
    - `opername` 发送人昵称
    - `timepoint` 时间点
    - `uservip_degree` 是否为VIP
    - `content` 弹幕内容
    
![qad_excel.png](.//media/qad_excel.png)

## TODO

- 基础图形生成
- 其他功能