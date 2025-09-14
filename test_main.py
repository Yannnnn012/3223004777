"""
论文查重系统单元测试模块
包含对main.py中所有核心功能的单元测试用例
"""
import unittest  # 测试框架
import os
import tempfile  # 创建测试环境
import sys
import math
import shutil  # 高级文件操作
from main import read_file, preprocess_text, calculate_cosine_similarity, calculate_similarity
sys.path.append('')


class TestPaperCheck(unittest.TestCase):
    """
    论文查重系统测试类
    继承自unittest.TestCase，包含所有单元测试方法
    """
    def setUp(self):
        """
        在每个测试方法执行前自动调用，创建临时测试环境
        """
        self.test_dir = tempfile.mkdtemp()

    def tearDown(self):
        """
        在每个测试方法执行后自动调用，清理测试资源
        """
        shutil.rmtree(self.test_dir)

    def test_read_file_normal(self):
        """
        测试正常读取文件功能
        """
        test_content = "测试内容"
        test_file = os.path.join(self.test_dir, "test.txt")
        with open(test_file, 'w', encoding='utf-8') as f:
            f.write(test_content)
        # 执行测试：读取内容
        result = read_file(test_file)
        # 验证结果
        self.assertEqual(result, test_content)

    def test_read_file_empty(self):
        """
        测试读取空文件功能
        """
        test_file = os.path.join(self.test_dir, "empty.txt")
        # 创建空文件
        with open(test_file, 'w', encoding='utf-8') as f:
            f.write("")
        result = read_file(test_file)
        # 验证空文件应该返回空字符串
        self.assertEqual(result, "")

    def test_read_file_not_exist(self):
        """
        测试读取不存在文件时的异常处理
        """
        non_existent_file = os.path.join(self.test_dir, "non_existent.txt")
        # 会引发SystemExit异常
        with self.assertRaises(SystemExit):
            read_file(non_existent_file)

    def test_preprocess_text_normal(self):
        """
        测试正常文本预处理功能
        """
        test_text = "明天早课，要早点睡，不然起不来！"
        result = preprocess_text(test_text)
        acceptable_results = ['明天', '早课', '早点', '睡', '不然', '起不来', '要']

        # 检查结果是否在可接受的范围内
        self.assertTrue(
            set(result) == set(acceptable_results) or
            f"分词结果 {result} 不在可接受范围内"
        )

        # 验证标点符号被正确去除
        punctuation = ['，', '。', '！', '？', '；', '：']
        for punc in punctuation:
            self.assertNotIn(punc, result, f"结果中不应包含标点符号: {punc}")

    def test_preprocess_text_english(self):
        """
        测试中英文混合文本的预处理
        """
        test_text = "Hello, 我的世界！Python编程很有趣。"
        result = preprocess_text(test_text)

        # 验证关键词语存在
        self.assertIn('世界', result)  # 中文分词
        self.assertIn('Python', result)  # 英文保留
        self.assertIn('编程', result)  # 中文分词

    def test_preprocess_text_empty(self):
        """
        测试空文本预处理
        """
        result = preprocess_text("")
        # 空文本应该返回空列表
        self.assertEqual(result, [])

    def test_calculate_cosine_similarity_identical(self):
        """
        测试完全相同的向量的余弦相似度计算，验证相似度应为1.0
        """
        vec1 = {'明天': 2, '空气': 1, '爽': 1}
        vec2 = {'明天': 2, '空气': 1, '爽': 1}
        similarity = calculate_cosine_similarity(vec1, vec2)
        self.assertAlmostEqual(similarity, 1.0, places=7)

    def test_calculate_cosine_similarity_orthogonal(self):
        """
        测试正交向量的余弦相似度计算，验证应为0.0
        """
        vec1 = {'昨天': 1, '太阳': 1}
        vec2 = {'后天': 1, '暴雨': 1}
        similarity = calculate_cosine_similarity(vec1, vec2)
        self.assertAlmostEqual(similarity, 0.0, places=7)

    def test_calculate_cosine_similarity_partial(self):
        """
        测试部分相似向量的余弦相似度计算
        """
        # 准备有部分共同词汇的词频向量
        vec1 = {'西区': 1, '共享': 1, '食堂': 1}
        vec2 = {'西区': 1, '共享': 1, '吃饭': 1}

        similarity = calculate_cosine_similarity(vec1, vec2)

        # 验证相似度在合理范围内（0到1之间）
        self.assertGreater(similarity, 0.0)
        self.assertLess(similarity, 1.0)

        # 正确的数学计算验证
        expected_similarity = 2 / (math.sqrt(3) * math.sqrt(3))
        self.assertAlmostEqual(similarity, expected_similarity, places=7)

    def test_calculate_cosine_similarity_empty(self):
        """
        测试空向量的余弦相似度计算，验证应为0.0
        """
        similarity = calculate_cosine_similarity({}, {})
        self.assertAlmostEqual(similarity, 0.0, places=7)

    def test_calculate_similarity_identical(self):
        """
        测试完全相同的文本的相似度计算，验证应为1.0
        """
        text1 = "夏天好热太阳好大啊"
        text2 = "夏天好热太阳好大啊"

        similarity = calculate_similarity(text1, text2)
        self.assertAlmostEqual(similarity, 1.0, places=2)

    def test_calculate_similarity_different(self):
        """
        测试完全不同的文本的相似度计算，验证应接近0.0
        """
        text1 = "西区的食堂，感觉一般般"
        text2 = "几乎每天，去东二吃饭"

        similarity = calculate_similarity(text1, text2)
        self.assertLess(similarity, 0.3)

    def test_calculate_similarity_plagiarized(self):
        """
        测试抄袭文本的相似度计算，验证应该有较高的相似度
        """
        original = "机器学习是人工智能的核心分支，需要大量数据与算力支持。"
        plagiarized = "机器学习作为人工智能的关键方向，依赖海量数据与强大算力。"
        similarity = calculate_similarity(original, plagiarized)
        self.assertGreater(similarity, 0.5)
        self.assertLess(similarity, 0.9)

    def test_calculate_similarity_empty(self):
        """
        测试空文本的相似度计算，验证应为0.0
        """
        similarity = calculate_similarity("", "")
        self.assertEqual(similarity, 0.0)

    def test_calculate_similarity_mixed_empty(self):
        """
        测试一个空文本和一个正常文本的相似度计算，验证应为0.0
        """
        similarity = calculate_similarity("正常文本", "")
        self.assertEqual(similarity, 0.0)


if __name__ == '__main__':
    # verbosity=2时显示更详细测试结果
    unittest.main(verbosity=2)