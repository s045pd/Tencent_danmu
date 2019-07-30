import json

import jieba
import pandas
from collections import Counter
from wordcloud import ImageColorGenerator, WordCloud, STOPWORDS

from conf import conf
from common import checkPath, checkTimes, error_log, initPath, read_stopwords
from log import success, error


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


# @error_log()
def create_singel_word_cloud(text, path, colors=None):
    filename = f"{path}.png"
    with checkTimes(msg=f"Saved {filename} "):
        if not text:
            error("none text!")
            return
        stopwords = set(STOPWORDS) | set(read_stopwords())
        list(map(stopwords.add, ["看", "都", "不"]))
        jiebares = jieba.cut(text)
        if conf.use_frequencies:
            jiebares = dict(
                filter(
                    lambda item: bool(item[0].strip())
                    and item[0].strip() not in stopwords,
                    Counter(jiebares).most_common(100000),
                )
            )
        else:
            jiebares = " ".join(jiebares)
        wc = WordCloud(
            background_color="black" if conf.is_dark else "white",
            font_path="HYQiHei-25J.ttf",
            max_words=2000,
            mask=colors,
            stopwords=stopwords,
            max_font_size=100,
            random_state=45,
        )
        (wc.generate_from_frequencies if conf.use_frequencies else wc.generate)(
            jiebares
        )
        wc.recolor(color_func=ImageColorGenerator(colors))
        wc.to_file(filename)
