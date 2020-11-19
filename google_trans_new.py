# author LuShan
# version : 0.6.0
import json,requests,random,re
from urllib.parse import quote
from six.moves import urllib
import urllib3
import logging
from constant import LANGUAGES,DEFAULT_SERVICE_URLS
import pdb

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

URLS_SUFFIX = [re.search('translate.google.(.*)',url.strip()).group(1) for url in DEFAULT_SERVICE_URLS]
URL_SUFFIX_DEFAULT = 'cn'

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

class google_translator:

    def __init__(self,lang_src='auto',lang_tgt='auto',url_suffix="cn"):
        if url_suffix not in URLS_SUFFIX:
            self.url_suffix = URL_SUFFIX_DEFAULT
        else:
            self.url_suffix = url_suffix
        url_base = "https://translate.google.{}".format(self.url_suffix)
        try:
            lang = LANGUAGES[lang_src]
        except :
            lang_src = 'auto'
        try:
            lang = LANGUAGES[lang_tgt]
        except :
            lang_src = 'auto'
        if lang_src == '' :
            lang_src = "auto"
        if lang_tgt == '':
            lang_tgt = 'auto'
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
            "Referer": "http://translate.google.{}/".format(self.url_suffix),
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
                    # pdb.set_trace()
                    # translation_part = re.search('\[(null,|true,|false,){5}(.*),\\\\".{2,4}\\\\",1,*\\\\".{2,4}\\\\"]\\\\n,\\\\".{2,4}\\\\"]', decoded_line).group(2)
                    translation_part = re.search('\[(null,|true,|false,){5}(.*),\\\\".{2,4}\\\\",1,\\\\".{2,4}\\\\\"]',decoded_line).group(2)

                    #translation_part = re.search('\[(null,|true,|false,){5}(.*),\\\\"en\\\\",1,*\\\\".{2,4}\\\\"]\\\\n,\\\\".{2,4}\\\\"]', decoded_line).group(2)
                    cleaned_translation_part = re.sub("false", "False",
                                                      re.sub("true", "True", re.sub("null", "None",
                                                                                    re.sub("\\\\", "",
                                                                                           re.sub(
                                                                                               "\\\\n",
                                                                                               "",
                                                                                               translation_part)))))
                    translated_sentences = [re.sub('\[\"|\", *\[', '', x) for x in
                                            re.findall("\[\"[^\[]+\", *\[", cleaned_translation_part)]
                    if translated_sentences == []:
                        return re.search("\"(.*)\"", cleaned_translation_part).group(1)
                    else:
                        return ' '.join(translated_sentences)
                r.raise_for_status()
            r.raise_for_status()
        except requests.exceptions.HTTPError as e:
            # Request successful, bad response
            log.debug(str(e))
            raise google_new_transError(tts=self, response=r)
        except requests.exceptions.RequestException as e:
            # Request failed
            log.debug(str(e))
            raise google_new_transError(tts=self)
