# coding:utf-8
# author LuShan
# version : 1.0.7
import json,requests,random,re
from urllib.parse import quote
from six.moves import urllib
import urllib3
import logging
from .constant import LANGUAGES,DEFAULT_SERVICE_URLS

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
    '''
    You can use 108 language in target and source,details view LANGUAGES.
    Target language: like 'en'、'zh'、'th'...

    :param url_suffix: The source text(s) to be translated. Batch translation is supported via sequence input.
                       The value should be one of the url_suffix listed in : `DEFAULT_SERVICE_URLS`
    :type url_suffix: UTF-8 :class:`str`; :class:`unicode`; string sequence (list, tuple, iterator, generator)

    :param text: The source text(s) to be translated.
    :type text: UTF-8 :class:`str`; :class:`unicode`;

    :param lang_tgt: The language to translate the source text into.
                     The value should be one of the language codes listed in : `LANGUAGES`
    :type lang_tgt: :class:`str`; :class:`unicode`

    :param lang_src: The language of the source text.
                    The value should be one of the language codes listed in :const:`googletrans.LANGUAGES`
                    If a language is not specified,
                    the system will attempt to identify the source language automatically.
    :type lang_src: :class:`str`; :class:`unicode`

    :param timeout: Timeout Will be used for every request.
    :type timeout: number or a double of numbers
    '''
    def __init__(self,url_suffix="cn",timeout=5):
        if url_suffix not in URLS_SUFFIX:
            self.url_suffix = URL_SUFFIX_DEFAULT
        else:
            self.url_suffix = url_suffix
        url_base = "https://translate.google.{}".format(self.url_suffix)
        self.url = url_base + "/_/TranslateWebserverUi/data/batchexecute"
        self.timeout = timeout

    def _package_rpc(self,text,lang_src='auto',lang_tgt='auto'):
        GOOGLE_TTS_RPC = ["MkEWBc"]
        parameter = [[text.strip(), lang_src, lang_tgt, True],[1]]
        escaped_parameter = json.dumps(parameter, separators=(',', ':'))
        rpc = [[[random.choice(GOOGLE_TTS_RPC), escaped_parameter, None, "generic"]]]
        espaced_rpc = json.dumps(rpc, separators=(',', ':'))
        # text_urldecode = quote(text.strip())
        freq_initial = "f.req={}&".format(quote(espaced_rpc))
        freq = freq_initial
        return freq

    def translate(self,text,lang_tgt='auto',lang_src='auto'):
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
        lang_src = lang_src
        lang_tgt = lang_tgt
        if type(text) == str:
            text = text.strip('\n').replace('\n',"").replace('\t','').replace('\\\"','')
        elif type(text) == list:
            return "type error"
        if len(text) >= 5000:
            return "Warning: Can only detect less than 5000 characters"
        if len(text) == 0:
            return ""
        headers = {
            "Referer": "http://translate.google.{}/".format(self.url_suffix),
            "User-Agent":
                "Mozilla/5.0 (Windows NT 10.0; WOW64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/47.0.2526.106 Safari/537.36",
            "Content-Type": "application/x-www-form-urlencoded;charset=utf-8"
        }
        freq = self._package_rpc(text,lang_src,lang_tgt)
        response = requests.Request(method='POST',
                                     url=self.url,
                                     data=freq,
                                     headers=headers)
        try:
            with requests.Session() as s:
                r = s.send(request=response.prepare(),
                           proxies=urllib.request.getproxies(),
                           verify=False,
                           timeout=self.timeout)
            for line in r.iter_lines(chunk_size=1024):
                decoded_line = line.decode('utf-8')
                if "MkEWBc" in decoded_line:
                    try :
                        sentences = re.findall(r'\[\\\"(.*?)\\\"\]',"[[\\\"" + decoded_line.split(r',[[\"')[-1])
                        data_got = ""
                        for sentence in sentences :
                            sentence = sentence.replace('\\\\\\','')
                            data_got += sentence.split(r"\",[\"")[0].strip() + ' '
                        return data_got
                    except :
                        return "ERROR"
            r.raise_for_status()
        except requests.exceptions.HTTPError as e:
            # Request successful, bad response
            log.debug(str(e))
            raise google_new_transError(tts=self, response=r)
        except requests.exceptions.RequestException as e:
            # Request failed
            log.debug(str(e))
            raise google_new_transError(tts=self)

    def detect(self,text):
        text = str(text).strip('\n').replace('\n',"").replace('\t','').replace('\\\"','')
        if len(text) >= 5000:
            return log.debug("Warning: Can only detect less than 5000 characters")
        if len(text) == 0:
            return ""
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
                    regex_str = r"\[\[\"wrb.fr\",\"MkEWBc\",\"\[\[(.*).*?,\[\[\["
                    try:
                        data_got = re.search(regex_str,decoded_line).group(1)
                    except Exception as e:
                        raise Exception("error")
                    data_got = data_got.split(",null,")[1].split('\\\"')[1]
                    data_got = data_got.replace('\\\\\\',"")
                    data_got = data_got.split('\\\"]')[0]
                    return [data_got,LANGUAGES[data_got.lower()]]
            r.raise_for_status()
        except requests.exceptions.HTTPError as e:
            # Request successful, bad response
            log.debug(str(e))
            raise google_new_transError(tts=self, response=r)
        except requests.exceptions.RequestException as e:
            # Request failed
            log.debug(str(e))
            raise google_new_transError(tts=self)
