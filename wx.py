from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

from data import *
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
                    'title': txt + '站',
                    'image': station_src(txt),
                    'url': 'https://wapbaike.baidu.com/item/%s站' % txt
                })
                reply.add_article({
                    'title': '途经车次',
                    'url': 'http://rail.qiangs.tech/page/station/%s' % txt
                })
            elif Line.objects.filter(line=txt):
                reply = ArticlesReply(message=msg)
                reply.add_article({
                    'title': txt + '次',
                    'url': 'http://rail.qiangs.tech/page/line/%s' % txt
                })
            else:
                reply = create_reply('小人不才，无法识别 ' + txt, msg)
        else:
            reply = create_reply('小人不才，无法识别 ' + msg.type, msg)
        response = HttpResponse(reply.render(), content_type="application/xml")
    return response
