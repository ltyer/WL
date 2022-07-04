import re
import os
import sys
import aiohttp
import asyncio
import json
import shutil
from pprint import pprint
from tqdm import tqdm


URL = sys.argv[1]


download_info = []

headers = {
    'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36',
    'Cookie':'PHPSESSID=24ros68hou8cjph1qculmeet10; PHPSESSID_NS_Sig=oenCV6mfmzpi-VS6; Hm_lvt_22a1fd52d71d27a688f488ceb244d3f8=1655025095,1655453284,1655453549; Hm_lvt_4e6c411431159e175bcf970ff0e95340=1655025095,1655453284,1655453550; Hm_lvt_0c942573ed1074fc5c46d882ec1d2f62=1655025095,1655453284,1655453550; Hm_lpvt_22a1fd52d71d27a688f488ceb244d3f8=1655453894; Hm_lpvt_4e6c411431159e175bcf970ff0e95340=1655453894; Hm_lpvt_0c942573ed1074fc5c46d882ec1d2f62=1655453894',
}

async def download():
    pathdir = download_info[0]['title'][0:20]
    if not os.path.exists(pathdir):
        os.mkdir(pathdir)
    else:
        shutil.rmtree(pathdir)

    l = len(download_info)
    with tqdm(total=l,colour="blue",desc="进度") as pbar:
        for info in download_info:
            title = re.sub('([^\u4e00-\u9fa5\u0030-\u0039\u0041-\u007a])', '', info['title'])
            url = f"https://www.ximalaya.com/revision/play/v1/audio?id={info['trackId']}&ptype=1"
            data = await getlist(url)
            data = json.loads(data)
            try:
                down_url = data['data']['src']
            except:
                print("VIP|限免 下载失败")
                exit(-1)
            data = await getlist(down_url)
            with open(os.path.join(pathdir, str(info['index']) + '.' + title+".m4a"),"wb") as f:
                f.write(data)
            pbar.set_postfix({'title': title[0:20]})
            pbar.update(1)

def getdowninfo(data):
    global albumTitle
    data = json.loads(data)
    if data['data']['tracks']:
        for i in data['data']['tracks']:
            info = {
                'index'     :   i['index'],
                'trackId'   :   i['trackId'],
                'title'     :   i['title'].replace(' ',''),
            }
            download_info.append(info)
    else:
        return False
    return True

async def getlist(url):
    async with asyncio.Semaphore(10):
        async with aiohttp.ClientSession() as session:
            async with session.get(url,headers=headers) as res:
                return await res.read()
            

async def main():
    albumid = re.findall("[0-9].*",URL)[0]
    pagenum = 1
    while True:
        url = f"https://www.ximalaya.com/revision/album/v1/getTracksList?albumId={albumid}&pageNum={pagenum}"
        data = await asyncio.ensure_future(getlist(url))
        if getdowninfo(data):
            pagenum += 1
        else:
            break
    global download_info
    download_info = sorted(download_info,key=lambda x: x['index'])
    pprint(download_info)
    print('\n')
    await download()

if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(main())
