"""应用启动脚本。

在根目录运行此脚本即可启动应用程序。
"""

import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# 运行主程序
if __name__ == "__main__":
    from src.main import main
    sys.exit(main())

