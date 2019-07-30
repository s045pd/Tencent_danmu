import json

import jieba
import pandas
from wordcloud import ImageColorGenerator, WordCloud, STOPWORDS

from common import checkPath, checkTimes, error_log, initPath
from log import success


def create_xlsx(datas, columns, filename="res.xlsx"):
    with checkTimes(msg=f"Created {filename} "):
        xlsx = pandas.DataFrame(datas)
        xlsx.rename(columns={_: __ for _, __ in enumerate(columns)}, inplace=True)
        writer = pandas.ExcelWriter(
            filename, engine="xlsxwriter", options={"strings_to_urls": False}
        )
        xlsx.to_excel(writer, "data")
        writer.save()


def create_json(datas, filename="res.json"):
    with checkTimes(msg=f"Saved {filename} "):
        with open(filename, "w") as f:
            f.write(json.dumps(datas, ensure_ascii=False, indent=4))


@error_log()
def create_singel_word_cloud(text, path, colors=None):
    filename = f"{path}.png"
    with checkTimes(msg=f"Saved {filename} "):
        if not text:
            return
        jiebares = " ".join(jieba.cut(text))
        wc = WordCloud(
            background_color="black",
            font_path="HYQiHei-25J.ttf",
            max_words=2000,
            mask=colors,
            stopwords=STOPWORDS,
            max_font_size=100,
            random_state=45,
        )
        wc.generate(jiebares)
        wc.recolor(color_func=ImageColorGenerator(colors))
        wc.to_file(filename)
