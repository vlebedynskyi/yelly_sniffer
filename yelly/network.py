# vim: tabstop=4 shiftwidth=4 softtabstop=4

# copyright [2013] [Vitalii Lebedynskyi]
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import urllib.request
import urllib.parse
import ssl

ssl._create_default_https_context = ssl._create_unverified_context


def do_get(url):
    if not url:
        raise ValueError("url cannot be empty")

    stream = urllib.request.urlopen(url)
    return stream.read().decode('utf-8')


def download_file(url, file):
    if not url:
        raise ValueError("url cannot be empty")

    stream = urllib.request.urlopen(url)
    with open(file, 'wb') as output:
        output.write(stream.read())

    return True


def get_random_headers():
    return {"Content-Encoding": "UTF-8", "Accept-Charset": "UTF-8"}