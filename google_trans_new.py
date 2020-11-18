# author LuShan
# version : 0.0.1
import json,requests,random,re
from urllib.parse import quote
from six.moves import urllib
import urllib3
import logging

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class google_new_transError(Exception):
    """Exception that uses context to present a meaningful error message"""

    def __init__(self, msg=None, **kwargs):
        self.tts = kwargs.pop('tts', None)
        self.rsp = kwargs.pop('response', None)
        if msg:
            self.msg = msg
        elif self.tts is not None:
            self.msg = self.infer_msg(self.tts, self.rsp)
        else:
            self.msg = None
        super(google_new_transError, self).__init__(self.msg)

    def infer_msg(self, tts, rsp=None):
        cause = "Unknown"

        if rsp is None:
            premise = "Failed to connect"

            # if tts.tld != 'com':
            #     host = _translate_url(tld=tts.tld)
            #     cause = "Host '{}' is not reachable".format(host)

        else:
            status = rsp.status_code
            reason = rsp.reason

            premise = "{:d} ({}) from TTS API".format(status, reason)

            if status == 403:
                cause = "Bad token or upstream API changes"
            elif status == 200 and not tts.lang_check:
                cause = "No audio stream in response. Unsupported language '%s'" % self.tts.lang
            elif status >= 500:
                cause = "Uptream API error. Try again later."

        return "{}. Probable cause: {}".format(premise, cause)

class google_new_trans:

    def __init__(self,lang_src='',lang_tgt='en',url_base="https://translate.google.cn"):
        self.lang_src = lang_src
        self.lang_tgt = lang_tgt
        self.url = url_base + "/_/TranslateWebserverUi/data/batchexecute"

    def _package_rpc(self,text):
        GOOGLE_TTS_RPC = ["MkEWBc"]
        parameter = [[text.strip(), self.lang_src, self.lang_tgt, True],[1]]
        escaped_parameter = json.dumps(parameter, separators=(',', ':'))
        rpc = [[[random.choice(GOOGLE_TTS_RPC), escaped_parameter, None, "generic"]]]
        espaced_rpc = json.dumps(rpc, separators=(',', ':'))
        text_urldecode = quote(text.strip())
        freq_initial = "f.req={}&".format(quote(espaced_rpc))
        freq = freq_initial.replace(text_urldecode,text)
        return freq

    def translate(self,text):
        headers = {
            "Referer": "http://translate.google.cn/",
            "User-Agent":
                "Mozilla/5.0 (Windows NT 10.0; WOW64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/47.0.2526.106 Safari/537.36",
            "Content-Type": "application/x-www-form-urlencoded;charset=utf-8"
        }
        freq = self._package_rpc(text)
        response = requests.Request(method='POST',
                                     url=self.url,
                                     data=freq,
                                     headers=headers)
        try:
            with requests.Session() as s:
                r = s.send(request=response.prepare(),
                           proxies=urllib.request.getproxies(),
                           verify=False,
                           timeout=5)
            for line in r.iter_lines(chunk_size=1024):
                decoded_line = line.decode('utf-8')
                if "MkEWBc" in decoded_line:
                    data_got = re.search(r',null,\[\[\\\"(.*?)\\\",\[',decoded_line).group(1)
                    data_got = data_got.replace('\\\\\\',"")
                    return data_got
            r.raise_for_status()
        except requests.exceptions.HTTPError as e:
            # Request successful, bad response
            log.debug(str(e))
            raise google_new_transError(tts=self, response=r)
        except requests.exceptions.RequestException as e:
            # Request failed
            log.debug(str(e))
            raise google_new_transError(tts=self)
