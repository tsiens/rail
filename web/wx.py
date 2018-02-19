from datetime import *

from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from wechatpy import *
from wechatpy.exceptions import *
from wechatpy.replies import *
from wechatpy.utils import *

from key import wx_token
from web.module import *

qiniu_img_url = 'http://qiniu.rail.qiangs.tech/station_img/%s.jpg?imageMogr2/auto-orient/thumbnail/!450x250r/gravity/Center/crop/x250/format/webp/blur/1x0/quality/75|imageslim&time=' + str(
    datetime.now().date())


@csrf_exempt  # 去除csrf认证
def wx(request):
    if request.method == 'GET':
        signature = request.GET.get('signature', '')
        timestamp = request.GET.get('timestamp', '')
        nonce = request.GET.get('nonce', '')
        echo_str = request.GET.get('echostr', '')
        try:
            check_signature(wx_token, signature, timestamp, nonce)
        except InvalidSignatureException:
            echo_str = 'error'
        response = HttpResponse(echo_str, content_type="text/plain")
    else:
        msg = parse_message(request.body)
        if msg.type == 'text':
            txt = msg.content.upper()
            n, data = search(txt)
            if txt == '日志':
                reply = ArticlesReply(message=msg, articles=[{
                    'title': '日志',
                    'url': 'http://rail.qiangs.tech/log'
                }])
            elif n > 0:
                articles = []
                for station in data['station'][:5]:
                    articles.append({
                        'title': '%s' % station,
                        'image': qiniu_img_url % station,
                        'url': 'http://rail.qiangs.tech/station/%s' % station
                    })
                for line in data['line'][:5 - len(articles) if len(articles) < 5 else 0]:
                    start, arrive = Line.objects.filter(line=line).values_list('start', 'arrive')[0]
                    articles.append({
                        'title': '%s次 %s-%s' % (line, start, arrive),
                        'image': qiniu_img_url % start,
                        'url': 'http://rail.qiangs.tech/line/%s' % line
                    })
                for city in data['city'][:5 - len(articles) if len(articles) < 5 else 0]:
                    articles.append({
                        'title': '%s' % city,
                        'url': 'http://rail.qiangs.tech/city/%s' % city
                    })
                reply = ArticlesReply(message=msg, articles=articles)
            else:
                k, v = luck()
                if k == 'city':
                    articles = [{
                        'title': '推荐 %s' % v,
                        'url': 'http://rail.qiangs.tech/city/%s' % v
                    }]
                elif k == 'station':
                    articles = [{
                        'title': '推荐 %s' % v,
                        'image': qiniu_img_url % v,
                        'url': 'http://rail.qiangs.tech/station/%s' % v
                    }]
                else:
                    start, arrive = Line.objects.filter(line=v).values_list('start', 'arrive')[0]
                    articles = [{
                        'title': '推荐 %s次 %s-%s' % (v, start, arrive),
                        'image': qiniu_img_url % start,
                        'url': 'http://rail.qiangs.tech/line/%s' % v
                    }]
                if txt != '推荐':
                    articles.append({'title': '小的不才，无法识别 “%s”' % txt})
                reply = ArticlesReply(message=msg, articles=articles)
        else:
            types = {'image': '图片', 'voice': '语音', 'video': '视频', 'music': '音乐', 'shortvideo': '小视频', 'location': '位置',
                     'link': '链接'}
            reply = create_reply('小的不才，无法识别 “%s”\nヾ(×× ) ﾂ' % types.get(msg.type, '消息'), msg)
        response = HttpResponse(reply.render(), content_type="application/xml")
    return response
