import re
import sys
from pathlib import Path

# 匹配 Markdown 图片语法：![alt](url)
# 参考：https://regex101.com/library/4LtaQZ
MD_IMAGE_RE = re.compile(
    r'!\[(?P<alt>[^\]]*)\]\((?P<url>[^)]+)\)'
)

# CSDN 图床常见域名
CSDN_DOMAINS = ('i-blog.csdnimg.cn', 'img-blog.csdnimg.cn')


def is_csdn_image_url(url: str) -> bool:
    """简单判断是不是 CSDN 图床链接"""
    url_lower = url.lower()
    return any(domain in url_lower for domain in CSDN_DOMAINS)


def extract_csdn_images(text: str):
    """
    从 Markdown 文本中提取 CSDN 图床图片，
    返回列表，每个元素是一个 dict：{'full': 原始字符串, 'alt': alt文本, 'url': 原URL}
    """
    matches = []
    for m in MD_IMAGE_RE.finditer(text):
        full = m.group(0)
        alt = m.group('alt')
        url = m.group('url')
        if is_csdn_image_url(url):
            matches.append({
                'full': full,
                'alt': alt,
                'url': url,
                'start': m.start(),
                'end': m.end(),
            })
    return matches


def replace_urls_in_text(text: str, replacements: list) -> str:
    """
    根据位置信息，一次性把所有 CSDN 图片链接替换为新链接。
    replacements: list of dict, 每个元素包含 {'start':, 'end':, 'new_full':}
    """
    # 按位置倒序排，避免替换后位置变化影响后面的替换
    replacements_sorted = sorted(replacements, key=lambda x: x['start'], reverse=True)
    for r in replacements_sorted:
        start, end = r['start'], r['end']
        new_full = r['new_full']
        text = text[:start] + new_full + text[end:]
    return text


def main():
    if len(sys.argv) != 2:
        print(f"用法: {sys.argv[0]} your_post.md")
        sys.exit(1)

    input_file = Path(sys.argv[1])
    if not input_file.is_file():
        print(f"文件不存在: {input_file}")
        sys.exit(1)

    text = input_file.read_text(encoding='utf-8')

    csdn_images = extract_csdn_images(text)
    if not csdn_images:
        print("没有找到 CSDN 图床链接。")
        return

    print(f"找到 {len(csdn_images)} 张 CSDN 图床图片，准备逐个替换...\n")

    replacements = []

    for i, img in enumerate(csdn_images, 1):
        print(f"[{i}/{len(csdn_images)}] 原链接:")
        print(f"  alt: {img['alt']}")
        print(f"  URL: {img['url']}")
        print(f"原始 Markdown: {img['full']}")
        print()

        # 读取你从自己图床粘贴回来的新链接
        # 你说格式是：![](https://qiniu.mingxuan.xin/picgo/20260302231931251.png)
        # 所以这里我们按同样格式来构造新的 Markdown 图片语法
        new_full = input("请粘贴新的图片 Markdown（例如 ![](https://...) ）: ").strip()

        # 简单校验一下是不是以 ![ 开头
        if not new_full.startswith('!['):
            print("警告：看起来不是 Markdown 图片语法，原样保留。")
            new_full = img['full']

        replacements.append({
            'start': img['start'],
            'end': img['end'],
            'new_full': new_full,
        })

    # 一次性替换所有链接
    new_text = replace_urls_in_text(text, replacements)

    # 写入新文件：在原文件名后加 _new
    output_file = input_file.with_name(input_file.stem + input_file.suffix)
    output_file.write_text(new_text, encoding='utf-8')

    print(f"\n替换完成，新文件已保存为: {output_file}")


if __name__ == '__main__':
    main()
