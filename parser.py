from log import info
import execjs


class Parser:
    @staticmethod
    def get_details(resp):

        core_data = execjs.compile(
            "function datas(){ var LIST_INFO="
            + resp.text.split("var LIST_INFO = ")[1].split("</script>")[0]
            + "return [LIST_INFO,COVER_INFO,VIDEO_INFO] }"
        )
        return core_data.call("datas")
