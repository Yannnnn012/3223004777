import os
import tempfile  # 临时文件和目录管理模块
import subprocess
import sys
import shutil
import unittest
import time


class IntegrationTest(unittest.TestCase):
    """集成测试类，测试整个论文查重系统的端到端功能"""
    def test_integration_basic(self):
        # 创建临时目录
        temp_dir = tempfile.mkdtemp()

        try:
            original_content = "今天天气真好，阳光明媚，我打算去公园散步，呼吸新鲜空气，享受这美好的周末时光。"
            plagiarized_content = "今天天气很不错，阳光灿烂，我计划去公园走走，呼吸一下新鲜空气，好好享受这个愉快的周末。"

            orig_file = os.path.join(temp_dir, "orig.txt")  # 原文
            plag_file = os.path.join(temp_dir, "org_add.txt")  # 抄袭版
            output_file = os.path.join(temp_dir, "result.txt")  # 结果

            with open(orig_file, 'w', encoding='utf-8') as f:
                f.write(original_content)
            with open(plag_file, 'w', encoding='utf-8') as f:
                f.write(plagiarized_content)

            # 运行主程序：python main.py [原文文件] [抄袭版文件] [输出文件]
            cmd = [sys.executable, 'main.py', orig_file, plag_file, output_file]
            # 执行命令，捕获输出和错误信息，设置30秒超时
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

            # 验证程序成功运行
            self.assertEqual(result.returncode, 0, f"程序运行失败: {result.stderr}")

            # 读取并检查输出结果
            with open(output_file, 'r', encoding='utf-8') as f:
                similarity = float(f.read().strip())

            # 验证结果在合理范围内
            self.assertGreaterEqual(similarity, 0.0)  # 相似度不小于0
            self.assertLessEqual(similarity, 1.0)  # 相似度不大于1
            self.assertGreater(similarity, 0.5)  # 抄袭文本应该有较高的相似度(>0.5)

            print(f"集成测试通过，相似度: {similarity:.2f}")

        finally:
            # 清理测试资源
            shutil.rmtree(temp_dir)

    def test_integration_identical(self):
        """测试完全相同的文本，相似度应该接近1.0"""
        temp_dir = tempfile.mkdtemp()

        try:
            content = "有机会的话就去冰岛看看吧"

            # 创建测试文件路径
            orig_file = os.path.join(temp_dir, "orig.txt")
            plag_file = os.path.join(temp_dir, "org_add.txt")
            output_file = os.path.join(temp_dir, "result.txt")

            # 写入相同的文本内容
            with open(orig_file, 'w', encoding='utf-8') as f:
                f.write(content)
            with open(plag_file, 'w', encoding='utf-8') as f:
                f.write(content)

            # 运行查重程序
            cmd = [sys.executable, 'main.py', orig_file, plag_file, output_file]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

            self.assertEqual(result.returncode, 0)  # 验证程序成功运行

            # 读取相似度结果
            with open(output_file, 'r', encoding='utf-8') as f:
                similarity = float(f.read().strip())

            # 验证相同文本的相似度接近1.0
            self.assertAlmostEqual(similarity, 1.0, places=1)

        finally:
            shutil.rmtree(temp_dir)

    def test_integration_different(self):
        """测试完全不同的文本，相似度应该很低(<0.3)"""
        temp_dir = tempfile.mkdtemp()

        try:
            # 创建完全不同主题的文本
            original_content = "今天是大太阳，出门要打太阳伞。"
            plagiarized_content = "天气预报说明天是暴雨，不能晒被子。"

            # 创建文件路径
            orig_file = os.path.join(temp_dir, "orig.txt")
            plag_file = os.path.join(temp_dir, "org_add.txt")
            output_file = os.path.join(temp_dir, "result.txt")

            # 写入文件
            with open(orig_file, 'w', encoding='utf-8') as f:
                f.write(original_content)
            with open(plag_file, 'w', encoding='utf-8') as f:
                f.write(plagiarized_content)

            # 运行查重程序
            cmd = [sys.executable, 'main.py', orig_file, plag_file, output_file]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

            self.assertEqual(result.returncode, 0)  # 验证程序成功运行

            # 读取相似度结果
            with open(output_file, 'r', encoding='utf-8') as f:
                similarity = float(f.read().strip())

            # 验证完全不同文本的相似度应该很低(<0.3)
            self.assertLess(similarity, 0.3)

        finally:
            shutil.rmtree(temp_dir)

    def test_integration_wrong_arguments(self):
        """测试命令行参数错误的情况，程序应该非零退出并显示用法信息"""
        cmd = [sys.executable, 'main.py', 'only_one_argument.txt']  # 只有一个参数的时候
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

        self.assertNotEqual(result.returncode, 0)
        # 检查stdout或stderr中是否有用法信息
        error_output = result.stderr + result.stdout
        self.assertIn("Usage", error_output)

    def test_integration_file_not_exist(self):
        """测试文件不存在的情况，程序应该正确处理错误"""
        temp_dir = tempfile.mkdtemp()
        try:
            nonexistent_file = os.path.join(temp_dir, "nonexistent.txt")
            output_file = os.path.join(temp_dir, "test/result.txt")

            cmd = [sys.executable, 'main.py', nonexistent_file, nonexistent_file, output_file]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

            self.assertNotEqual(result.returncode, 0)  # 应该失败（返回码不为0）
            error_output = result.stderr + result.stdout
            self.assertIn("Error reading file", error_output)

        finally:
            shutil.rmtree(temp_dir)

    def test_integration_performance(self):
        """测试性能：确保程序在5秒内完成大规模文本处理"""
        temp_dir = tempfile.mkdtemp()
        try:
            # 生成较大的测试文本
            content = "生活需要有所规划。" * 1000

            orig_file = os.path.join(temp_dir, "orig.txt")
            plag_file = os.path.join(temp_dir, "org_add.txt")
            output_file = os.path.join(temp_dir, "result.txt")
            with open(orig_file, 'w', encoding='utf-8') as f:
                f.write(content)
            with open(plag_file, 'w', encoding='utf-8') as f:
                f.write(content)

            start_time = time.time()  # 记录时间

            # 运行查重程序
            cmd = [sys.executable, 'main.py', orig_file, plag_file, output_file]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

            end_time = time.time()
            elapsed_time = end_time - start_time  # 计算耗时

            self.assertEqual(result.returncode, 0)
            self.assertLess(elapsed_time, 5.0, f"处理时间{elapsed_time:.2f}秒超过5秒限制")
            print(f"性能测试通过，耗时: {elapsed_time:.2f}秒")

        finally:
            shutil.rmtree(temp_dir)


def run_integration_tests():
    """运行所有集成测试并返回测试结果"""
    # 创建测试套件，加载IntegrationTest类中的所有测试方法
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(IntegrationTest)

    # 运行测试，verbosity=2显示详细测试结果
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_integration_tests()  # 运行所有集成测试
    # 根据测试结果退出：0表示成功，1表示失败
    sys.exit(0 if success else 1)