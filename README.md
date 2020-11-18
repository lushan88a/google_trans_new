# google_trans_new

A free and unlimited python tools for google translate api.  
It's very easy to use and solve the problem that the old api which use tk value cannot be used.  
***
  
  
Installation
====
```
pip install google_trans_new
```
***
  
  
Basic Usage
=====
```python  
from google_new_trans import google_new_trans  
  
translator = google_new_trans('th','en','https://translate.google.cn')  
# <Translate lang_tgt=ko lang_src=en url=https://translate.google.cn >  
translate_text = translator.translate('สวัสดีจีน')  
# <Translate text=สวัสดีจีน >  
print(translate_text)
# Hello china
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
