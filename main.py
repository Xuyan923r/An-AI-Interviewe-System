# -*- coding: utf-8 -*-

import sys

# 跨平台UTF-8编码设置
if sys.platform.startswith('win'):
    import locale
    try:
        locale.setlocale(locale.LC_ALL, 'zh_CN.UTF-8')
    except Exception:
        try:
            locale.setlocale(locale.LC_ALL, 'Chinese_China.936')
        except Exception:
            pass

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')

from ai_interview.app import run_app


if __name__ == "__main__":
    run_app()


