"""统计分析模块。

导出统计分析功能。
"""

from src.features.analytics.reports import (
    Analytics,
    AnalyticsError
)

__all__ = [
    'Analytics',
    'AnalyticsError',
]
