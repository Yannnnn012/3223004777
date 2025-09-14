"""
论文查重系统主程序模块
实现基于余弦相似度的中文文本相似度检测算法
"""
import sys
import jieba  # 中文分词库，用于将中文文本切分成词语
import re  # 正则表达式库，用于文本清洗和去除标点符号
from collections import Counter  # 计数器，统计词频
import math  # 数学库


def read_file(file_path):
    """
    读取指定路径的文本文件内容
    Args:
        file_path (str): 要读取的文件路径
    Returns:
        str: 文件的内容字符串
    Raises:
        SystemExit: 如果文件读取失败，打印错误信息并退出程序
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read().strip()  # 读取内容并去除首尾空白字符
        return content
    except Exception as e:
        print(f"Error reading file {file_path}: {e}")
        sys.exit(1)


def preprocess_text(text):
    """
    对文本进行预处理：去除标点符号并进行中文分词
    Args:
        text (str): 原始文本字符串
    Returns:
        list: 分词后的词语列表
    """
    # 文本清洗和去除标点符号
    text = re.sub(r'[^\w\s]', '', text)
    # 用jieba分词
    words = jieba.cut(text)
    # 转换为列表
    return list(words)


def calculate_cosine_similarity(vec1, vec2):
    """
    计算两个词频向量的余弦相似度
    余弦相似度公式：cosθ = (A·B) / (||A|| * ||B||)
    Args:
        vec1 (dict): 第一个文本的词频字典 {词语: 频率}
        vec2 (dict): 第二个文本的词频字典 {词语: 频率}
    Returns:
        float: 余弦相似度值，范围[0, 1]
    """
    # 获取两个字典的所有词汇的并集，确保向量维度一致
    all_words = set(vec1.keys()).union(set(vec2.keys()))

    # 根据词汇表创建数值向量，缺失的词语频率为0
    vector1 = [vec1.get(word, 0) for word in all_words]
    vector2 = [vec2.get(word, 0) for word in all_words]

    # 计算两个向量的点积（对应位置相乘后求和）
    dot_product = sum(v1 * v2 for v1, v2 in zip(vector1, vector2))

    # 计算两个向量的模长（欧几里得范数）
    magnitude1 = math.sqrt(sum(v * v for v in vector1))
    magnitude2 = math.sqrt(sum(v * v for v in vector2))

    # 处理除零错误：如果任一向量模长为0，相似度为0
    if magnitude1 == 0 or magnitude2 == 0:
        return 0.0

    # 返回余弦相似度值
    return dot_product / (magnitude1 * magnitude2)
# import numpy as np
#
#
# def calculate_cosine_similarity(vec1: dict, vec2: dict):
#     """优化后：采用 NumPy 向量化，循环全部下沉到 C 层"""
#     if not vec1 or not vec2:
#         return 0.0
#
#     # 取并集词汇表
#     words = list(set(vec1) | set(vec2))
#     # 一次性构造向量
#     a = np.array([vec1.get(w, 0) for w in words], dtype=np.float32)
#     b = np.array([vec2.get(w, 0) for w in words], dtype=np.float32)
#
#     dot = np.dot(a, b)          # 点积
#     norm_a = np.linalg.norm(a)  # 模长
#     norm_b = np.linalg.norm(b)
#
#     return (dot / (norm_a * norm_b)) if norm_a and norm_b else 0.0


def calculate_similarity(original_text, copied_text):
    """
    计算两段文本的相似度
    处理流程：
    1. 文本分词
    2. 统计词频
    3. 计算余弦相似度
    Returns:
        float: 两段文本的相似度，范围[0, 1]
    """
    # 分词
    original_words = preprocess_text(original_text)
    copied_words = preprocess_text(copied_text)

    # 统计词频
    original_freq = Counter(original_words)
    copied_freq = Counter(copied_words)

    # 计算两个词频向量的余弦相似度
    similarity = calculate_cosine_similarity(original_freq, copied_freq)
    return similarity


def main():
    """
    命令行参数格式：
    python main.py [原文文件] [抄袭版论文的文件] [答案文件]
    """
    # 检查命令行参数数量是否正确（程序名 + 3个文件路径 = 4个参数）
    if len(sys.argv) != 4:
        print("Usage: python main.py [原文文件] [抄袭版论文的文件] [答案文件]")
        sys.exit(1)

    original_file = sys.argv[1]  # 原文文件路径
    copied_file = sys.argv[2]  # 抄袭版文件路径
    output_file = sys.argv[3]  # 结果输出文件路径

    # 读取文本内容
    original_text = read_file(original_file)
    copied_text = read_file(copied_file)

    # 计算两段文本的相似度
    similarity = calculate_similarity(original_text, copied_text)

    try:
        # 将相似度结果写入输出文件，保留两位小数
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("{:.2f}".format(similarity))
    except Exception as e:
        # 文件写入失败时，打印错误信息并退出程序
        print(f"Error writing to output file: {e}")
        sys.exit(1)


# Python程序入口：当直接运行此脚本时执行main函数
if __name__ == "__main__":
    main()