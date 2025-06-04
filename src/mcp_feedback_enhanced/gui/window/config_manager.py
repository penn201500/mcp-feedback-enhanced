#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
配置管理器
===========

負責處理用戶配置的載入、保存和管理。
"""

import json
from pathlib import Path
from typing import Dict, Any

from ...debug import gui_debug_log as debug_log


class ConfigManager:
    """配置管理器"""

    def __init__(self):
        self._config_file = self._get_config_file_path()
        self._config_cache = {}
        self._load_config()

    def _get_config_file_path(self) -> Path:
        """獲取配置文件路徑"""
        config_dir = Path.home() / ".config" / "mcp-feedback-enhanced"
        config_dir.mkdir(parents=True, exist_ok=True)
        return config_dir / "ui_settings.json"

    def _load_config(self) -> None:
        """載入配置"""
        try:
            if self._config_file.exists():
                with open(self._config_file, 'r', encoding='utf-8') as f:
                    self._config_cache = json.load(f)
                debug_log("配置文件載入成功")
            else:
                self._config_cache = {}
                debug_log("配置文件不存在，使用預設配置")
        except Exception as e:
            debug_log(f"載入配置失敗: {e}")
            self._config_cache = {}

    def _save_config(self) -> None:
        """保存配置"""
        try:
            with open(self._config_file, 'w', encoding='utf-8') as f:
                json.dump(self._config_cache, f, ensure_ascii=False, indent=2)
            debug_log("配置文件保存成功")
        except Exception as e:
            debug_log(f"保存配置失敗: {e}")

    def get(self, key: str, default: Any = None) -> Any:
        """獲取配置值"""
        return self._config_cache.get(key, default)

    def set(self, key: str, value: Any) -> None:
        """設置配置值"""
        self._config_cache[key] = value
        self._save_config()

    def update_partial_config(self, updates: Dict[str, Any]) -> None:
        """批量更新配置項目，只保存指定的設定而不影響其他參數"""
        try:
            # 重新載入當前磁碟上的配置，確保我們有最新的數據
            current_config = {}
            if self._config_file.exists():
                with open(self._config_file, 'r', encoding='utf-8') as f:
                    current_config = json.load(f)

            # 只更新指定的項目
            for key, value in updates.items():
                current_config[key] = value
                # 同時更新內存緩存
                self._config_cache[key] = value

            # 保存到文件
            with open(self._config_file, 'w', encoding='utf-8') as f:
                json.dump(current_config, f, ensure_ascii=False, indent=2)

            debug_log(f"部分配置已更新: {list(updates.keys())}")

        except Exception as e:
            debug_log(f"更新部分配置失敗: {e}")

    def get_layout_mode(self) -> bool:
        """獲取佈局模式（False=分離模式，True=合併模式）"""
        return self.get('combined_mode', False)

    def set_layout_mode(self, combined_mode: bool) -> None:
        """設置佈局模式"""
        self.update_partial_config({'combined_mode': combined_mode})
        debug_log(f"佈局模式設置: {'合併模式' if combined_mode else '分離模式'}")

    def get_layout_orientation(self) -> str:
        """獲取佈局方向（vertical=垂直（上下），horizontal=水平（左右））"""
        return self.get('layout_orientation', 'vertical')

    def set_layout_orientation(self, orientation: str) -> None:
        """設置佈局方向"""
        if orientation not in ['vertical', 'horizontal']:
            orientation = 'vertical'
        self.update_partial_config({'layout_orientation': orientation})
        debug_log(f"佈局方向設置: {'垂直（上下）' if orientation == 'vertical' else '水平（左右）'}")

    def get_language(self) -> str:
        """獲取語言設置"""
        return self.get('language', 'zh-TW')

    def set_language(self, language: str) -> None:
        """設置語言"""
        self.update_partial_config({'language': language})
        debug_log(f"語言設置: {language}")

    def get_splitter_sizes(self, splitter_name: str) -> list:
        """獲取分割器尺寸"""
        sizes = self.get(f'splitter_sizes.{splitter_name}', [])
        if sizes:
            debug_log(f"載入分割器 {splitter_name} 尺寸: {sizes}")
        return sizes

    def set_splitter_sizes(self, splitter_name: str, sizes: list) -> None:
        """設置分割器尺寸"""
        self.update_partial_config({f'splitter_sizes.{splitter_name}': sizes})
        debug_log(f"保存分割器 {splitter_name} 尺寸: {sizes}")

    def get_window_geometry(self) -> dict:
        """獲取窗口幾何信息"""
        geometry = self.get('window_geometry', {})
        if geometry:
            debug_log(f"載入窗口幾何信息: {geometry}")
        return geometry

    def set_window_geometry(self, geometry: dict) -> None:
        """設置窗口幾何信息（使用部分更新避免覆蓋其他設定）"""
        self.update_partial_config({'window_geometry': geometry})
        debug_log(f"保存窗口幾何信息: {geometry}")

    def get_always_center_window(self) -> bool:
        """獲取總是在主螢幕中心顯示視窗的設置"""
        return self.get('always_center_window', False)

    def set_always_center_window(self, always_center: bool) -> None:
        """設置總是在主螢幕中心顯示視窗"""
        self.update_partial_config({'always_center_window': always_center})
        debug_log(f"視窗定位設置: {'總是中心顯示' if always_center else '智能定位'}")

    def reset_settings(self) -> None:
        """重置所有設定到預設值"""
        try:
            # 清空配置緩存
            self._config_cache = {}

            # 刪除配置文件
            if self._config_file.exists():
                self._config_file.unlink()
                debug_log("配置文件已刪除")

            debug_log("所有設定已重置到預設值")

        except Exception as e:
            debug_log(f"重置設定失敗: {e}")
            raise

    # ===== 窗口行為設置 =====

    def get_setting(self, key: str, default: Any = None) -> Any:
        """獲取任意設置值（支持點分隔的層級key）"""
        keys = key.split('.')
        value = self._config_cache

        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default

        return value

    def set_setting(self, key: str, value: Any) -> None:
        """設置任意設置值（支持點分隔的層級key）"""
        keys = key.split('.')
        config = self._config_cache

        # 確保路徑存在
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            elif not isinstance(config[k], dict):
                config[k] = {}
            config = config[k]

        # 設置最終值
        config[keys[-1]] = value
        self._save_config()
        debug_log(f"設置已更新: {key} = {value}")

    def get_window_auto_focus(self) -> bool:
        """獲取窗口自動聚焦設置"""
        return self.get_setting('window.auto_focus', True)

    def set_window_auto_focus(self, auto_focus: bool) -> None:
        """設置窗口自動聚焦"""
        self.set_setting('window.auto_focus', auto_focus)
        debug_log(f"窗口自動聚焦設置: {auto_focus}")

    def get_window_stay_on_top(self) -> bool:
        """獲取窗口保持最前面設置"""
        return self.get_setting('window.stay_on_top', False)

    def set_window_stay_on_top(self, stay_on_top: bool) -> None:
        """設置窗口保持最前面"""
        self.set_setting('window.stay_on_top', stay_on_top)
        debug_log(f"窗口保持最前面設置: {stay_on_top}")

    def get_window_auto_raise(self) -> bool:
        """獲取窗口自動置頂設置"""
        return self.get_setting('window.auto_raise', True)

    def set_window_auto_raise(self, auto_raise: bool) -> None:
        """設置窗口自動置頂"""
        self.set_setting('window.auto_raise', auto_raise)
        debug_log(f"窗口自動置頂設置: {auto_raise}")

    def get_window_minimize_on_focus_loss(self) -> bool:
        """獲取失去焦點時最小化設置"""
        return self.get_setting('window.minimize_on_focus_loss', False)

    def set_window_minimize_on_focus_loss(self, minimize: bool) -> None:
        """設置失去焦點時最小化"""
        self.set_setting('window.minimize_on_focus_loss', minimize)
        debug_log(f"失去焦點時最小化設置: {minimize}")

    def get_window_global_shortcuts_enabled(self) -> bool:
        """獲取全局快捷鍵啟用設置"""
        return self.get_setting('window.global_shortcuts_enabled', False)

    def set_window_global_shortcuts_enabled(self, enabled: bool) -> None:
        """設置全局快捷鍵啟用"""
        self.set_setting('window.global_shortcuts_enabled', enabled)
        debug_log(f"全局快捷鍵啟用設置: {enabled}")

    def get_window_opacity(self) -> float:
        """獲取窗口透明度設置"""
        return self.get_setting('window.opacity', 1.0)

    def set_window_opacity(self, opacity: float) -> None:
        """設置窗口透明度（0.0-1.0）"""
        opacity = max(0.1, min(1.0, opacity))  # 限制在0.1-1.0範圍內
        self.set_setting('window.opacity', opacity)
        debug_log(f"窗口透明度設置: {opacity}")

    def get_default_window_settings(self) -> dict:
        """獲取默認窗口設置"""
        return {
            'auto_focus': True,
            'stay_on_top': False,
            'auto_raise': True,
            'minimize_on_focus_loss': False,
            'global_shortcuts_enabled': False,
            'opacity': 1.0
        }
