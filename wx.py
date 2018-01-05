from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

from web.models import *
from key import wx_token

from wechatpy import *
from wechatpy.exceptions import *
from wechatpy.utils import *
from wechatpy.replies import *


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
            if Station.objects.filter(cn=txt):
                reply = ArticlesReply(message=msg)
                reply.add_article({
                    'title': '车站: %s站' % txt,
                    'image': Station.objects.get(cn=txt).image_url,
                    'url': 'https://wapbaike.baidu.com/item/%s站' % txt
                })
                reply.add_article({
                    'title': '途经车次',
                    'url': 'http://rail.qiangs.tech/page/station/%s' % txt
                })
            elif Line.objects.filter(line=txt):
                reply = ArticlesReply(message=msg)
                start = Line.objects.get(line=txt).start
                arrive = Line.objects.get(line=txt).arrive
                reply.add_article({
                    'title': '车次: %s次 %s-%s' % (txt, start, arrive),
                    'image': Station.objects.get(cn=start).image_url,
                    'url': 'http://rail.qiangs.tech/page/line/%s' % txt
                })
            elif len(txt.split(' ')) == 3:
                start, arrive, date = txt.split(' ')
                reply = ArticlesReply(message=msg)
                reply.add_article({
                    'title': '余票: %s号 %s-%s' % (date, start, arrive),
                    'image': Station.objects.get(cn=start).image_url,
                    'url': 'http://rail.qiangs.tech/page/ticket/%s|%s|%s' % (start, arrive, date)
                })
            else:
                reply = create_reply('小的不才，无法识别 “%s” ' % txt +
                                     '\n查车站 如发送 “杭州东”' +
                                     '\n查车次 如发送 “D1”' +
                                     '\n查余票 如发送 “杭州 上海 6”（6号）', msg)
        else:
            reply = create_reply('小的不才，无法识别 ' + msg.type, msg)
        response = HttpResponse(reply.render(), content_type="application/xml")
    return response
