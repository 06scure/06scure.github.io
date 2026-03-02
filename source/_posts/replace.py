import os
import sys

def clean_default_description(folder_path):
    """
    遍历文件夹，删除 md 文件中的 "在这里插入图片描述" 文字
    """
    target_text = "在这里插入图片描述"
    count_files = 0
    count_replacements = 0
    
    print(f"开始扫描文件夹: {folder_path}")
    print("-" * 40)

    # os.walk 可以递归遍历所有子文件夹
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            # 只处理 .md 文件
            if file.lower().endswith('.md'):
                file_path = os.path.join(root, file)
                
                try:
                    # 读取文件内容
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # 如果包含目标文字
                    if target_text in content:
                        # 计算替换次数
                        occurrences = content.count(target_text)
                        
                        # 进行替换（删除）
                        new_content = content.replace(target_text, "")
                        
                        # 写回文件
                        with open(file_path, 'w', encoding='utf-8') as f:
                            f.write(new_content)
                        
                        print(f"[处理] {file_path}")
                        print(f"   -> 删除了 {occurrences} 处描述文字")
                        
                        count_files += 1
                        count_replacements += occurrences
                        
                except Exception as e:
                    print(f"[错误] 无法处理文件 {file_path}: {e}")

    print("-" * 40)
    print(f"处理完成！")
    print(f"共修改了 {count_files} 个文件，删除了 {count_replacements} 处目标文字。")

if __name__ == "__main__":
    # 获取用户输入的路径，默认为当前目录
    if len(sys.argv) > 1:
        target_folder = sys.argv[1]
    else:
        target_folder = os.getcwd()
    
    if not os.path.isdir(target_folder):
        print(f"错误：提供的路径不是一个有效的文件夹: {target_folder}")
        sys.exit(1)
        
    clean_default_description(target_folder)
