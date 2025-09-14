import os
import multiprocessing

# 方法1：使用os模块
cpu_count_os = os.cpu_count()
print(f"CPU核心数(os.cpu_count()): {cpu_count_os}")

# 方法2：使用multiprocessing模块
cpu_count_mp = multiprocessing.cpu_count()
print(f"CPU核心数(multiprocessing.cpu_count()): {cpu_count_mp}")

# 方法3：获取更详细的信息
import psutil  # 需要安装: pip install psutil
if hasattr(psutil, 'cpu_count'):
    physical_cores = psutil.cpu_count(logical=False)  # 物理核心数
    logical_cores = psutil.cpu_count(logical=True)    # 逻辑核心数(超线程)
    print(f"物理核心数: {physical_cores}")
    print(f"逻辑核心数: {logical_cores}")