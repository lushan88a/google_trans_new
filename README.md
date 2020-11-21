# google_trans_new
### Version 1.1.0

A free and unlimited python API for google translate.  
It's very easy to use and solve the problem that the old api which use tk value cannot be used.  
This interface is for academic use only, please do not use it for commercial use.  
  
Version 1.1.0 fixed many issues.
***
  
  
Installation
====
```
pip install google_trans_new
```
***
  
  
Basic Usage
=====
### Transalte
```python  
from google_trans_new import google_translator  
  
translator = google_translator(url_suffix='cn',timeout=5)  
# <Translate url_suffix=cn timeout=5>  
#  default parameter : url_suffix="cn" timeout=5
#  url_suffix="cn" use in https://translate.google.{}/ 
translate_text = translator.translate('สวัสดีจีน',lang_tgt='en',lang_src='th' )  
# <Translate text=สวัสดีจีน lang_tgt=th lang_src=en>  
#  default parameter : lang_src=auto lang_tgt=auto 
#  API can automatically identify the src translation language, so you don’t need to set lang_src
print(translate_text)
-> Hello china
```
### Detect
```python
from google_trans_new import google_translator  
  
detector = google_translator()  
detect_result = detector.detect('สวัสดีจีน')
# <Detect text=สวัสดีจีน >  
print(detect_result)
-> ['th', 'thai']
```
***

Prerequisites
====
* **Python >=3.6**  
* **requests**  
* **six**  
***
  
  
License
====
google_trans_new is licensed under the MIT License. The terms are as follows:  

```
MIT License  

Copyright (c) 2020 lushan88a  

Permission is hereby granted, free of charge, to any person obtaining a copy  
of this software and associated documentation files (the "Software"), to deal  
in the Software without restriction, including without limitation the rights  
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell  
copies of the Software, and to permit persons to whom the Software is  
furnished to do so, subject to the following conditions:  

The above copyright notice and this permission notice shall be included in all  
copies or substantial portions of the Software.  

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR  
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,  
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE  
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER  
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,  
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE  
SOFTWARE.  
```
