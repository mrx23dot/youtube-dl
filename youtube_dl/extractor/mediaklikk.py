# coding: utf-8
from __future__ import unicode_literals

from .common import InfoExtractor
from ..compat import compat_urllib_parse_unquote
import re


class MediaKlikkIE(InfoExtractor):
    # Named regular expression group: (?P<name>...) used for referencing match as 'id'
    _VALID_URL = r'https?:\/\/(?:www\.)?(?:mediaklikk|m4sport|hirado)\.hu\/.*\/(?P<id>[^\/]+)\/?'

    _TESTS = [{
        'url': 'https://mediaklikk.hu/adal2020/video/2020/03/07/a-dal-donto/',
        'md5': 'bae2df47983139d831fef87b40f3ccff',
        'info_dict': {
            'id': 'a-dal-donto',
            'ext': 'mp4',
            'title': 'A Dal 2020, Döntő',
            # no thumbnail extractable
        }
    }, {
        'url': 'https://m4sport.hu/bl-video/uefa-bajnokok-ligaja-selejtezo-ferencvarosi-tc-gnk-dinamo-zagreb-merkozes/',
        'md5': '1d03d9ce5156a0f48a8f0856e9190ead',
        'info_dict': {
            'id': 'uefa-bajnokok-ligaja-selejtezo-ferencvarosi-tc-gnk-dinamo-zagreb-merkozes',
            'ext': 'mp4',
            'title': 'UEFA Bajnokok Ligája selejtező: Ferencvárosi TC - GNK Dinamo Zagreb mérkőzés',
            # no thumbnail extractable
        }
    }, {
        'url': 'https://hirado.hu/video/2020/09/21/az-operativ-torzs-rendkivuli-sajtotajekoztatoja-2020-szeptember-21',
        'md5': 'f00b6bd229f60f58ea52b88b91efd239',
        'info_dict': {
            'id': 'az-operativ-torzs-rendkivuli-sajtotajekoztatoja-2020-szeptember-21',
            'ext': 'mp4',
            'title': 'Az operatív törzs rendkívüli sajtótájékoztatója, 2020. szeptember 21.',
            # no thumbnail extractable
        }
    }]

    def _real_extract(self, url):
        mobj = re.match(self._VALID_URL, url)
        video_id = mobj.group('id')
        display_id = video_id  # we only have one id in url..
        webpage = self._download_webpage(url, video_id)

        pattern = r"mtva_player_manager\.player\(document.getElementById\(.*\),\s?(\{.*\}).*\);"
        info_json = self._html_search_regex(pattern, webpage, 'info_json')
        info_meta = self._parse_json(compat_urllib_parse_unquote(info_json), None)

        info_ret = {
            '_type': 'video',
            'title': info_meta.get('title') or video_id or self._og_search_title(webpage),
            'ext': 'mp4',
            'display_id': display_id,
            'id': video_id
        }

        if 'series' in info_meta:
            info_ret['series'] = info_meta['series']
        info_meta['video'] = info_meta['token']
        del info_meta['token']
        playerpage = self._download_webpage('https://player.mediaklikk.hu/playernew/player.php',
                                            video_id, query=info_meta)
        pattern = r"\"file\": \"(\\/\\/.*playlist\.m3u8)\","
        playlist_url = 'https:' + compat_urllib_parse_unquote(
            self._html_search_regex(pattern, playerpage, 'playlist_url'))\
            .replace('\\/', '/')
        formats = self._extract_wowza_formats(
            playlist_url, video_id, skip_protocols=['f4m', 'smil', 'dash'])
        self._sort_formats(formats)
        info_ret['formats'] = formats

        return info_ret
