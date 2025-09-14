# 论文查重系统

### 项目描述
基于余弦相似度算法的中文论文查重系统。

### 功能特性
- 中文文本预处理和分词
- 基于词频的余弦相似度计算
- 文件输入输出支持
- 完整的单元测试和集成测试

### 安装依赖
```bash
pip install -r requirements.txt
```
### 查看性能
```bash
python -m cProfile -o profile_stats.prof main.py test/orig.txt test/org_add.txt output.txt
snakeviz profile_stats.prof
```
### 查看测试覆盖率
```bash
# 运行单元测试
coverage run -m unittest test_main.py
# 运行集成测试
coverage run -m unittest test_integration.py
# 运行所有测试
coverage run -m unittest discover
coverage report
coverage html
start htmlcov/index.html
```
### 查重
```bash
python main.py test/orig.txt test/org_add.txt test/result.txt
```
