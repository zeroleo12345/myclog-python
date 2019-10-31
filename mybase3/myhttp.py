from urllib.parse import quote
"""
# 方法1:
    urllib.parse.quote('#company#')

# 方法2:
    urllib.parse.urlencode({'#company#':'Yunpian', '#code#':'1234'})
"""

def url_encode(url):
    return quote(url)

