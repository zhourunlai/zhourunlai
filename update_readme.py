import httpx
import os
import re


def write_content(part, content):
    file = "./README.md"
    pattern = f"<!--PART:{part}-->[\\S\\s]*\\s<!--PART:{part}-->"
    whole_content = f"<!--PART:{part}-->\n{content}\n<!--PART:{part}-->"
    with open(file, 'r+') as f:
        content = f.read()
        content_new = re.sub(pattern, whole_content, content, flags = re.M)
        f.seek(0)
        f.write(content_new)
        f.truncate()


def build_span(percent, chunk):
    span = ""
    i = 0
    while i < 100 / chunk:
        if percent >= chunk:
            span += "█"
        elif percent >= chunk / 2:
            span += "▓"
        elif percent >= 0:
            span += "▒"
        else:
            span += "░"
        percent -= chunk
        i += 1
    return span


def fetch_wakatime_part():
    wakatime_key = os.getenv('WAKATIME_KEY')
    if not wakatime_key:
        return
    url = f'https://wakatime.com/api/v1/users/current/stats/last_7_days?api_key={wakatime_key}'
    result = httpx.get(url)
    data = result.json()
    languages = data['data']['languages']
    max_name_len = 0
    max_text_len = 0
    chunk = 10
    content = ''
    for lang in languages:
        max_name_len = max(len(lang['name']), max_name_len)
        max_text_len = max(len(lang['text']), max_text_len)
    for lang in languages:
        pattern = f'%-{max_name_len}s %-{max_text_len}s %-{chunk}s %.2f%%\n'
        content += pattern % (lang['name'], lang['text'], build_span(lang['percent'], chunk), lang['percent'])
    return f'```text\n{content}```'


def main():
    content = fetch_wakatime_part()
    write_content('wakatime', content)


if __name__ == "__main__":
    main()
