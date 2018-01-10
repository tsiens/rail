from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

from web.models import *
from key import wx_token
import re

from wechatpy import *
from wechatpy.exceptions import *
from wechatpy.utils import *
from wechatpy.replies import *

qiniu_img_url = 'http://qiniu.rail.qiangs.tech/station_img/%s.jpg?imageMogr2/auto-orient/thumbnail/!450x250r/gravity/Center/crop/x250/format/webp/blur/1x0/quality/75|imageslim'
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
        if msg.type == 'event' and msg.event == 'subscribe':
            reply = create_reply('日出东方,唯我不败\n东方教主,文成武德\n千秋万载,一统江湖\n12308,咔咔就是发\n扣“神功”可得武林秘籍', msg)
        elif msg.type == 'text':
            txt = msg.content.upper()
            if txt == '日志':
                reply = ArticlesReply(message=msg, articles=[{
                    'title': '日志',
                    'url': 'http://rail.qiangs.tech/log'
                }])
            elif txt == '神功':
                reply = create_reply('吸尘大法：\n车站 扣“杭州东”\n车次 敲“D1”\n余票 打“杭州 上海 6”（6号）', msg)
            elif Station.objects.filter(cn=txt):
                reply = ArticlesReply(message=msg, articles=[{
                    'title': '车站: %s站' % txt,
                    'image': qiniu_img_url % txt,
                    'url': 'http://rail.qiangs.tech/station/%s' % txt
                }, {
                    'title': '百度百科',
                    'url': 'https://wapbaike.baidu.com/item/%s站' % txt
                }])
            elif Line.objects.filter(line=txt):
                start = Line.objects.get(line=txt).start
                arrive = Line.objects.get(line=txt).arrive
                reply = ArticlesReply(message=msg, articles=[{
                    'title': '车次: %s次 %s-%s' % (txt, start, arrive),
                    'image': qiniu_img_url % txt,
                    'url': 'http://rail.qiangs.tech/line/%s' % txt
                }])
            elif len(txt.split(' ')) == 3:
                start, arrive, date = txt.split(' ')
                reply = ArticlesReply(message=msg, articles=[{
                    'title': '余票: %s号 %s-%s' % (date, start, arrive),
                    'image': qiniu_img_url % txt,
                    'url': 'http://rail.qiangs.tech/ticket/%s/%s/%s' % (start, arrive, date)
                }])
            else:
                reply = create_reply('小的不才，无法识别 “%s”\n回复“神功”可解锁更多姿势哦\nヾ(×× ) ﾂ' % txt, msg)
        else:
            types = {'image': '图片', 'voice': '语音', 'video': '视频', 'music': '音乐', 'shortvideo': '小视频', 'location': '位置',
                     'link': '链接'}
            reply = create_reply('小的不才，无法识别 “%s”\n回复“神功”可解锁更多姿势哦\nヾ(×× ) ﾂ' % types.get(msg.type, '消息'), msg)
        response = HttpResponse(reply.render(), content_type="application/xml")
    return response
