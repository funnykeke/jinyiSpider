import sys
import time
import requests
import pathlib

sys.path.extend((str(parent.absolute()) for parent in pathlib.Path(__file__).parents))
# 获取座位表
findSetMap = 'https://www.jycinema.com/frontUIWebapp/appserver/seatInformationMapService/findSeatMap'
# 获取所有场次
findItemSku = 'https://www.jycinema.com/frontUIWebapp/appserver/commonItemSkuService/findItemSku'

session = requests.Session()
session.headers.update({
    "Accept": "application/json, text/plain, */*",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "zh-CN,zh;q=0.9",
    "Connection": "keep-alive",
    "Content-Type": "application/x-www-form-urlencoded;charset=UTF-8",
    "Host": "www.jycinema.com",
    "Origin": "https://www.jycinema.com",
    "Referer": "https://www.jycinema.com/wap/",
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1 Edg/120.0.0.0"
})
findItemSkuParams = {'params': '{"cinemaId":"630","filmIdAlt":"4890","type":"queryItemSku","showtime":"2023-12-31",'
                               '"memberLevelName":"","channelId":7,"channelCode":"J0005","memberId":""}'}

res = session.post(findItemSku, data=findItemSkuParams).json()
datas = res['data'][1:]
while 1:
    hasFree = False
    for index, data in enumerate(datas):
        sessionId = data['sessionOutId']
        cinemaOutId = data['cinemaOuterId']
        skuId = data['skuId']
        channelId = data['channelId']
        channelCode = data['channelCode']
        findSetMapParams = {
            'params': f'{{"sessionId":"{sessionId}","cinemaOutId":"{cinemaOutId}","skuId":{skuId},"channelId":{channelId},"channelCode":"{channelCode}","memberId":""}}'
        }
        # 所有空闲的位置
        allFreeSeat = []
        try:
            setMap = session.post(findSetMap, data=findSetMapParams)
            data = setMap.json()
            if '座位图刷新成功' in data['msg']:
                seatMapInfo = data['data']['seatMapInfo']
                for seatList in seatMapInfo:
                    for seat in seatList['data']:
                        if seat['status'] == '0' and seat['physicalName'] > 4:
                            allFreeSeat.append(seat)
        except:
            print('请求/解析失败')
            time.sleep(10)
        # 通过每一排的座位号（id）和座位排号（physicalName）判断同一排是否存在连坐的座位
        for seat in allFreeSeat:
            for seat2 in allFreeSeat:
                if seat['physicalName'] == seat2['physicalName'] and seat['id'] + 1 == seat2['id']:
                    print(seat, seat2)
                    hasFree = True
        if hasFree:
            requests.get(
                f'http://www.pushplus.plus/send?token=??&title=速点第{index + 1}个链接&template=html')
            break
        else:
            print('没有连坐座位！')
    # 等待5秒
    time.sleep(5)
