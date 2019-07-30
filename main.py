import argparse
import json
import logging
import os
import time
from io import BytesIO
from parser import Parser
from pprint import pprint


import asks
import click
import jieba
import pandas
import trio
from common import (
    addfailed,
    addsucess,
    addtotal,
    addupdate,
    checkTimes,
    initPath,
    checkPath,
    get_pic_array,
)
from conf import conf
from exporter import create_json, create_xlsx, create_singel_word_cloud
from log import error, info, makeStatus, success, warning
from PIL import Image
from pyquery import PyQuery as jq
from wordcloud import ImageColorGenerator, WordCloud

asks.init("trio")


class Spider(object):
    def __init__(self, *args, **kwargs):
        super(Spider, self).__init__()
        self.__results = {}
        self.__cover_info = []
        self.__root_path = "videos"
        self.__res_file_name = "res.json"
        self.__res_xlsx_name = "res.xlsx"
        self.__res_png_name = "res"
        self.__limits = trio.CapacityLimiter(conf.maxConnections * 10)

    async def __init_session(self):
        self.__async_session = asks.Session(connections=conf.maxConnections)
        self.__async_session.headers = conf.fakeHeader

    async def __get_video_list(self, url):
        """Get video's HASH id list

        Base on the url to fetch the response body and get the key data by pyquery


        Demo: https://v.qq.com/x/cover/p69wlzli02uqwms/d0023ka5gj7.html    

        Args:
            url: target video' url 
        """
        try:
            info(f"Url: {url}")
            response = await self.__async_session.get(url)
            self.__list_info, self.__cover_info, self.__video_info = Parser.get_details(
                response
            )
            self.__root_path = f'{self.__root_path}/{self.__cover_info["title"]}'
            info(f"Name: [{self.__root_path}]")
            initPath(self.__root_path)
            create_json(self.__list_info, f"{self.__root_path}/list_info.json")
            create_json(self.__cover_info, f"{self.__root_path}/cover_info.json")
            create_json(self.__video_info, f"{self.__root_path}/video_info.json")
        except Exception as e:
            raise e

    async def __get_reg_id(self, vid_data):
        """ Get video's register id 

        Args:
            vid_data: like following dictionary 
            {
                "F": 2,
                "V": "c00231h58yj",
                "E": 1
            }

        """
        _, vid, number = [value for key, value in vid_data.items()]
        jquery_id = f"jQuery_{str(int(time.time()))}"
        response = await self.__async_session.get(
            f"https://bullet.video.qq.com/fcgi-bin/target/regist?callback={jquery_id}&otype=json&vid={vid}&cid=p69wlzli02uqwms&lid=&g_tk=1115548900&_={str(int(time.time()))}"
        )
        targetid = json.loads(response.text[len(jquery_id) + 1 : -1]).get("targetid")
        if targetid:
            success(f"targetid [{targetid}]")
            self.__results[vid] = {
                "number": number,
                "targetid": targetid,
                "datas": {},
                "single_max_count": 0 if not conf.max_time else conf.max_time,
            }

    async def __get_sigle_danmu(self, item):
        """ Get only one video's Danmu  """

        key, dataset = item
        jquery_id = f"jQuery_{str(int(time.time()))}"

        async def GetItem(item, point=0):
            async with self.__limits:
                try:
                    single_max_count = item["single_max_count"]
                    url = f"https://mfm.video.qq.com/danmu?otype=json&callback={jquery_id}&timestamp={point}&target_id={item['targetid']}&count=80&second_count=5&session_key=45094%2C118%2C{str(int(time.time()))}&_={str(int(time.time()))}"
                    addupdate()
                    warning(url)
                    response = await self.__async_session.get(url)
                    assert response.status_code == 200
                    jsondata = json.loads(
                        response.text[len(jquery_id) + 1 : -1], strict=False
                    )
                    assert jsondata["comments"]
                    for item in jsondata["comments"]:
                        self.__results[key]["datas"][item["commentid"]] = item
                        addtotal()

                    if single_max_count == 0:
                        self.__results[key].update(
                            {i: jsondata[i] for i in ["tol_up", "single_max_count"]}
                        )
                        self.__results[key]["single_max_count"] = jsondata[
                            "single_max_count"
                        ]
                    addsucess()
                    success(url)
                except Exception as e:
                    addfailed()
                    # raise e

        async with trio.open_nursery() as nursery:
            nursery.start_soon(GetItem, dataset)

        async with trio.open_nursery() as nursery:
            for stamp in range(0, dataset["single_max_count"] + 30, 30):
                nursery.start_soon(GetItem, dataset, stamp)

    async def __get_all_danmus(self, datas):
        """ Fetch all the danmus with asynchronize networks  """

        async with trio.open_nursery() as nursery:
            for vid_data in datas["nomal_ids"]:
                nursery.start_soon(self.__get_reg_id, vid_data)

        info(f"All Data Nums: [{len(self.__results.keys())}]")
        async with trio.open_nursery() as nursery:
            for item in self.__results.items():
                nursery.start_soon(self.__get_sigle_danmu, item)

    def create_word_clouds(self):
        """
        demo: {"n0023msdsmb": {
                "number": 29,
                "targetid": "1871591968",
                "datas": {
                    "6258341153647188912": {
                        "commentid": "6258341153647188912",
                        "content": "我来了，我困了",
                        "upcount": 2,
                        "isfriend": 0,
                        "isop": 0,
                        "isself": 0,
                        "timepoint": 15,
                        "headurl": "http://q4.qlogo.cn/g?b=qq&k=QAyiafGCYJbfG8lRKTsVTFQ&s=40",
                        "opername": "沉默Deheart",
                        "bb_bcolor": "0x985850",
                        "bb_head": "http://i.gtimg.cn/qqlive/images/20160602/pic_luhan.png",
                        "bb_level": "http://i.gtimg.cn/qqlive/images/20170104/i1483523275_1.jpg",
                        "content_style": ""
                    }}}}
        """
        image_path = f"{self.__root_path}/imgs"
        word_cloud_path = f"{self.__root_path}/words"
        initPath(image_path)
        initPath(word_cloud_path)

        img_array = get_pic_array(
            self.__cover_info["vertical_pic_url"], f"{image_path}/vertical_pic.png"
        )

        all_words = ""
        for indexHash, item in self.__results.items():
            words = " ".join(
                map(lambda data: data[1]["content"], list(item["datas"].items()))
            )
            all_words += words
            create_singel_word_cloud(
                words, f"{word_cloud_path}/{item['number']}", img_array
            )
        create_singel_word_cloud(
            all_words, f"{self.__root_path}/{self.__res_png_name}", img_array
        )

    def create_danmu_xlsx(self, title):
        xlsx_path = f"{self.__root_path}/xlsx"
        initPath(xlsx_path)
        tmp_data = []
        data_length = len(self.__results.keys())
        tmp_data.append(title)
        for did, item in self.__results.items():
            tmp_data_bottom = []
            for tid, titem in item["datas"].items():
                tmp_data_bottom.append([titem[_] for _ in title])
            tmp_data.extend(tmp_data_bottom)
            if data_length > 2:
                create_xlsx(
                    tmp_data_bottom, title, f"{xlsx_path}/{item['number']}.xlsx"
                )
        create_xlsx(tmp_data, title, f"{self.__root_path}/{self.__res_xlsx_name}")

    def run(self):
        # https://v.qq.com/x/cover/3fvg46217gw800n/h0030qj4fov.html
        if "https://v.qq.com/x/cover/" not in conf.url:
            error("not a video link!")
            exit()
        datas_path = None
        try:
            trio.run(self.__init_session)
            trio.run(self.__get_video_list, conf.url)
            datas_path = f"{self.__root_path}/{self.__res_file_name}"
            if conf.new or not checkPath(datas_path):
                trio.run(self.__get_all_danmus, self.__cover_info)
            else:
                with open(datas_path, "r") as file:
                    self.__results = json.loads(file.read())
            # tmp_res = sorted(self.__results.items(), key=lambda item: item[1]['number'])
            if conf.need_excel:
                self.create_danmu_xlsx(
                    [
                        "upcount",
                        "commentid",
                        "opername",
                        "timepoint",
                        "uservip_degree",
                        "content",
                    ]
                )
            if conf.need_words:
                self.create_word_clouds()
            if conf.need_graph:
                pass
        finally:
            create_json(self.__results, datas_path)


@click.command()
@click.option(
    "-u",
    "--url",
    default="https://v.qq.com/x/cover/p69wlzli02uqwms/d0023ka5gj7.html",
    help="指定目标URL",
    type=str,
)
@click.option("-t", "--max_time", default=None, help="指定每集时间长度，不宜过大(针对vip视频)", type=int)
@click.option("-v", "--vip", is_flag=True, help="vip默认设置15000秒")
@click.option("-c", "--cons", default=None, help="爬行并发数量", type=int)
@click.option("-n", "--new", is_flag=True, help="不使用缓存生成")
@click.option("-e", "--excel", is_flag=True, help="是否生成Excel")
@click.option("-w", "--words", is_flag=True, help="是否生成词云")
@click.option("-f", "--use_frequencies", is_flag=True, help="是否使用词频")
@click.option("-b", "--words_background", default=None, help="指定词云背景图")
@click.option("-d", "--is_dark", is_flag=True, help="是否为纯黑底色")
@click.option("-g", "--graph", is_flag=True, help="是否生成分析图")
def main(
    url,
    max_time,
    vip,
    cons,
    new,
    excel,
    words,
    use_frequencies,
    words_background,
    is_dark,
    graph,
):
    if url:
        conf.url = url
    if max_time:
        conf.max_time = max_time
    if vip:
        conf.max_time = 20000
    if new:
        conf.new = new
    if cons:
        conf.maxConnections = cons
    if excel:
        conf.need_excel = excel
    if words:
        conf.need_words = words
    if use_frequencies:
        conf.use_frequencies = use_frequencies
    if words_background:
        conf.words_background = words_background
    if is_dark:
        conf.is_dark = is_dark
    if graph:
        conf.need_graph = graph
    Spider().run()


if __name__ == "__main__":
    with checkTimes():
        try:
            main()
        except KeyboardInterrupt:
            pass
        except Exception as e:
            raise e
        finally:
            info("finished")
