import re
import pycurl
import requests
import m3u8
import sys
import os
import multiprocessing
from random import random


def get_link(id, file_name, output):
    link = ""
    num = 0
    file_name_parts = file_name.split('_')
    vod_id = file_name_parts[-1].split('.')[0]
    for line in open(os.path.join(output, ('chunks_' + vod_id + '.txt')), 'rb'):
        temppath = output + r'\temp'
        num += 1
        if num % 32 == id:
            tempname = file_name.replace('.', ('_' + str(num) + '.'))
            if not os.path.exists(os.path.join(temppath, tempname)):
                link = line
                break;
    return (link.split('\n')[0], num)


def update_progress(lock, completed_num):  # , link, flag, output, tempname):
    lock.acquire()
    completed_num.value += 1
    # if flag == 0:
    #    with open(os.path.join(output, ('fails.txt')), 'ab+') as fails:
    #        fails.write("%s\n" % (link + ' ' + tempname))
    lock.release()


def download_progress(id, file_name, output, completed_num, count):
    headers = ['User-Agent:Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_5)\
                                AppleWebKit 537.36 (KHTML, like Gecko) Chrome', \
               'Accept:text/html,application/xhtml+xml,application/xml;\
                            q=0.9,image/webp,*/*;q=0.8']
    lock = multiprocessing.Lock()
    while True:
        link, num = get_link(id, file_name, output)
        tempname = file_name.replace('.', ('_' + str(num) + '.'))
        temppath = os.path.join(output + r'\temp', tempname)
        if link == "":
            print 'end'
            break;
        url_error = 0
        print "Downloading: %s" % (file_name + '_' + str(num))
        if not os.path.exists(output + "\\temp"):
            os.makedirs(output + "\\temp")

        part = open(temppath, 'wb')
        curl = pycurl.Curl()
        curl.setopt(pycurl.WRITEDATA, part)
        curl.setopt(pycurl.FOLLOWLOCATION, True)
        curl.setopt(pycurl.URL, link)
        curl.setopt(pycurl.SSL_VERIFYPEER, False)
        curl.setopt(pycurl.SSL_VERIFYHOST, False)
        curl.setopt(pycurl.HTTPHEADER, headers)
        curl.setopt(pycurl.TIMEOUT, 600)
        while True:
            try:
                curl.perform()
            except Exception, e:
                url_error += 1
                print "urlerror " + str(url_error)
                print "error on: " + str(num)
                print e
                # curl.close()
                # part.close()
                # update_progress(lock, completed_num, link, 0, output, tempname)
                # print "%f%% jumped" % ((completed_num.value / count) * 100)
                # break
                # import traceback
                #
                # traceback.print_exc(file=sys.stdout)
                # raise e
            else:
                break
        curl.close()
        part.close()
        update_progress(lock, completed_num)  # , link, 1, output, tempname)
        print "%f%%" % ((completed_num.value / count) * 100)


if __name__ == '__main__':
    count = 0
    completed = 0
    # VOD_id = raw_input("Enter Twitch Video ID: ")
    # url = "https://www.twitch.tv/a_seagull/v/" + VOD_id
    url = raw_input("Enter Url: ")
    start = 0
    end = sys.maxint
    output = r"E:\twitch\a_seagull"
    temppath = output + r'\temp'
    if not os.path.exists(output):
        os.makedirs(output)
    if not os.path.exists(temppath):
        os.makedirs(temppath)

    # headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_5)\
    #                              AppleWebKit 537.36 (KHTML, like Gecko) Chrome", \
    #            "Accept": "text/html,application/xhtml+xml,application/xml;\
    #                           q=0.9,image/webp,*/*;q=0.8"}

    headers = ['User-Agent:Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_5)\
                            AppleWebKit 537.36 (KHTML, like Gecko) Chrome', \
               'Accept:text/html,application/xhtml+xml,application/xml;\
                            q=0.9,image/webp,*/*;q=0.8']

    try:
        common_headers = {'Authorization': 'OAuth %s' % open(os.path.expanduser('~/.twitch_token')).readline()}
    except Exception, e:
        common_headers = {}

    # new API specific variables
    _chunk_re = "(.+\.ts)\?start_offset=(\d+)&end_offset=(\d+)"
    _simple_chunk_re = "(.+\.ts)"
    _vod_api_url = "https://api.twitch.tv/api/vods/{}/access_token?adblock=true&need_https=true&platform=web&player_type=site&oauth_token=7seonif5w3sivvaqdbd8trawssjzmr"  # https://api.twitch.tv/api/vods/89333620/access_token?adblock=true&need_https=true&platform=web&player_type=site&oauth_token=7seonif5w3sivvaqdbd8trawssjzmr
    _index_api_url = "http://usher.ttvnw.net/vod/{}"

    _url_re = re.compile(r"""
                http(s)?://
                (?:
                    (?P<subdomain>\w+)
                    \.
                )?
                twitch.tv
                /
                (?P<channel>[^/]+)
                (?:
                    /
                    (?P<video_type>[bcv])
                    /
                    (?P<video_id>\d+)
                )?
            """, re.VERBOSE)

    match = _url_re.match(url).groupdict()
    channel = match.get("channel").lower()
    subdomain = match.get("subdomain")
    video_type = match.get("video_type")
    video_id = match.get("video_id")

    name = '%s_%s.mp4' % (channel, video_id)
    prog_name = os.path.join(output, ('progress_' + video_id + '.txt'))
    transport_stream_file_name = name.replace('.mp4', '.ts')
    if video_type == 'v':
        if not os.path.exists(prog_name):
            # Get access code
            url = _vod_api_url.format(video_id)
            r = requests.get(url, headers=common_headers)
            data = r.json()

            # Fetch vod index
            url = _index_api_url.format(video_id)
            payload = {'nauth': data['token'], 'nauthsig': data['sig'], 'allow_source': True, 'allow_spectre': False,
                       "player": "twitchweb", "p": int(random() * 999999), "allow_audio_only": True, "type": "any"}
            r = requests.get(url, params=payload, headers=common_headers)
            m = m3u8.loads(r.content)
            index_url = m.playlists[0].uri
            index = m3u8.load(index_url)

            # Get the piece we need
            position = 0
            chunks = []

            for seg in index.segments:
                # Add duration of current segment
                position += seg.duration

                # Check if we have gotten to the start of the clip
                if position < start:
                    continue

                # Extract clip name and byte range
                p = re.match(_chunk_re, seg.absolute_uri)
                # match for playlists without byte offsets
                if not p:
                    p = re.match(_simple_chunk_re, seg.absolute_uri)
                    filename = p.groups()[0]
                    start_byte = 0
                    end_byte = 0
                else:
                    filename, start_byte, end_byte = p.groups()

                chunks.append([filename, start_byte, end_byte])

                # Check if we have reached the end of clip
                if position > end:
                    break

            # download clip chunks and merge into single file
            count = 0
            with open(os.path.join(output, ('chunks_' + video_id + '.txt')), 'wb+') as cf:
                for c in chunks:
                    video_url = "{}?start_offset={}&end_offset={}".format(*c)
                    cf.write('%s\n' % video_url)
                    count += 1
            with open(prog_name, 'wb+') as prog:
                prog.write('%s\n' % count)

        elif os.path.exists(prog_name):
            with open(prog_name, 'rb') as prog:
                count = int(prog.readline().split('\n')[0])
                if count is None:
                    sys.exit(1)
            for num in range(1, count + 1):
                tempname = transport_stream_file_name.replace('.', ('_' + str(num) + '.'))

                if os.path.exists(os.path.join(temppath, tempname)):
                    completed += 1
            print "Save detected, continue downloading..."
            print count

        code = open(os.path.join(output, transport_stream_file_name), 'wb+')

        # VOD_links = multiprocessing.Array('str', len(VOD_chunks), VOD_chunks, lock=True)
        # progress_status = multiprocessing.Array('int', len(progress), progress, lock=True)
        completed_num = multiprocessing.Value('d', 0.0)
        completed_num.value = float(completed)
        multi_num = 32

        process = []
        for i in range(multi_num):
            download = multiprocessing.Process(target=download_progress, args=(i, transport_stream_file_name, output,
                                                                               completed_num, count))
            download.daemon = True
            process.append(download)

        for i in range(len(process)):
            process[i].start()

        for i in range(len(process)):
            process[i].join()

        print "Download completed!"

        print "Merging video parts..."
        video_parts = os.listdir(output + r'\temp')

        video_parts_ordered = [1] * len(video_parts)

        for i in range(len(video_parts)):
            temp = video_parts[i].split('_')[-1]
            temp2 = video_parts[i].split('_')[-2]
            temp = temp.split('.')[0]
            temp = int(temp)
            if temp2 == video_id:
                video_parts_ordered[temp - 1] = video_parts[i]

        for files in video_parts_ordered:
            with open(os.path.join(output + r'\temp', files), 'rb') as video_part:
                buffer = video_part.read()
                code.write(buffer)
                print files + " finished!"
        code.close()
        print "Completed!"
        # print "Coding video..."
        # os.popen3('ffmpeg -i %s -bsf:a aac_adtstoasc -c copy %s' % (transport_stream_file_name, name))
        # print "Coding completed!"
