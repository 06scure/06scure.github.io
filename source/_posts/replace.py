import re
import sys
import os
from pathlib import Path

# 正则匹配 Markdown 图片语法：![alt](url)
MD_IMAGE_RE = re.compile(r'!\[(?P<alt>[^\]]*)\]\((?P<url>[^)]+)\)')

# CSDN 图床域名特征
CSDN_DOMAINS = ('i-blog.csdnimg.cn', 'img-blog.csdnimg.cn')

def is_csdn_image_url(url: str) -> bool:
    """判断是否为 CSDN 图床链接"""
    return any(domain in url.lower() for domain in CSDN_DOMAINS)

def extract_csdn_images(text: str):
    """
    提取所有 CSDN 图片信息。
    返回列表，每项包含：原始完整字符串、alt文本、url、位置(start, end)
    """
    matches = []
    for m in MD_IMAGE_RE.finditer(text):
        url = m.group('url')
        if is_csdn_image_url(url):
            matches.append({
                'full': m.group(0),
                'alt': m.group('alt'),
                'url': url,
                'start': m.start(),
                'end': m.end()
            })
    return matches

def main():
    if len(sys.argv) != 2:
        print(f"用法: python {sys.argv[0]} <你的博文.md>")
        sys.exit(1)

    input_file = Path(sys.argv[1])
    if not input_file.exists():
        print(f"错误：找不到文件 {input_file}")
        sys.exit(1)

    # 读取文件
    content = input_file.read_text(encoding='utf-8')
    
    # 1. 提取所有 CSDN 图片
    images = extract_csdn_images(content)
    
    if not images:
        print("未在文件中检测到 CSDN 图床链接。")
        return

    print(f"检测到 {len(images)} 张 CSDN 图片：")
    print("-" * 40)
    for i, img in enumerate(images, 1):
        print(f"{img['url']}")
    print("-" * 40)
    
    print("\n请复制上方链接进行批量上传。")
    print("上传完成后，请将新链接粘贴到下方（可以是 Markdown 格式 ![]() 或纯链接）。")
    print("可以一次性粘贴多行，按 Ctrl+D (Linux/Mac) 或 Ctrl+Z (Windows) 并回车结束输入：\n")

    # 2. 读取用户粘贴的新链接（支持多行输入）
    new_lines = []
    try:
        while True:
            line = input()
            if line.strip():
                new_lines.append(line.strip())
    except EOFError:
        pass

    # 3. 解析用户输入的新链接
    # 正则用于从用户粘贴的 ![](url) 或纯 url 中提取网址
    url_extractor = re.compile(r'\((http[^)]+)\)|^(http[^\s]+)$')
    
    new_urls = []
    for line in new_lines:
        # 尝试提取链接
        m = url_extractor.search(line)
        if m:
            # 优先取分组1（括号内的），否则取分组2（纯链接）
            url = m.group(1) if m.group(1) else m.group(2)
            new_urls.append(url)
        else:
            # 如果格式完全不对，给出警告但尝试整行当作链接（视情况可去掉）
            print(f"警告：无法解析这行内容，将忽略：{line}")

    # 4. 校验数量是否一致
    if len(new_urls) != len(images):
        print(f"\n错误：检测到 {len(images)} 张图，但提供了 {len(new_urls)} 个新链接。请检查数量是否匹配。")
        sys.exit(1)

    # 5. 执行替换（从后往前替换，防止位置索引错乱）
    # 这样我们只需要原文件内容对象 content，不需要额外创建列表
    for i in range(len(images) - 1, -1, -1):
        old_info = images[i]
        new_url = new_urls[i]
        
        # 关键点：组合新的 Markdown 标签，保留原来的 alt 文本
        # old_info['alt'] 即原来的文字描述
        new_markdown = f"![{old_info['alt']}]({new_url})"
        
        # 替换原文本
        content = content[:old_info['start']] + new_markdown + content[old_info['end']:]

    # 6. 保存新文件
    output_file = input_file.with_name(f"{input_file.stem}{input_file.suffix}")
    output_file.write_text(content, encoding='utf-8')
    print(f"\n成功！新文件已保存至: {output_file}")

if __name__ == '__main__':
    main()
