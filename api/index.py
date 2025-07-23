#!/usr/bin/env python3
"""
Vercel用エントリーポイント
"""

import sys
import os

# 親ディレクトリをパスに追加
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app

# Vercelのサーバーレス関数として動作
handler = app