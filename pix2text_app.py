import string
import time
import random
from pathlib import Path
import threading
import subprocess
import os
import tempfile
import gc
import sys
import logging

import yaml
from PIL import ImageGrab, Image
import pyperclip
import rumps
from pynput import keyboard

# 延迟导入 Pix2Text，降低启动内存占用
# 配置日志记录
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

SUCCESS_NT_FORM = {
    "title": "Success!",
    "subtitle": "Success! Copied to clipboard.",
    "message": "",
}

ERROR_NT_FORM = {
    "title": "Fail!",
    "subtitle": "Error! You didn't copy the screenshot.",
    "message": "",
}

CONFIG = yaml.safe_load(open("./config.yaml", "r", encoding="utf-8"))
OUTPUT_MD_ROOT_DIR = Path(CONFIG["output_md_root_dir"])
OUTPUT_MD_ROOT_DIR.mkdir(exist_ok=True)
OUTPUT_DEBUG_DIR = Path(CONFIG["output_debug_dir"])
OUTPUT_DEBUG_DIR.mkdir(exist_ok=True)
TEXT_FORMULA_RESIZED_SHAPE = CONFIG["text_formula_resized_shape"]
PAGE_RESIZED_SHAPE = CONFIG["page_resized_shape"]


class Pix2TextApplication(rumps.App):
    def __init__(self, name):
        super(Pix2TextApplication, self).__init__(
            name=name, icon="./icons/p2t-logo.png", quit_button="Quit"
        )
        # 延迟加载 Pix2Text，减少启动内存占用
        self.p2t = None

        # 设置热键监听器
        self.hotkey_listener = None
        self.start_keyboard_listener()
        
    def _get_p2t(self):
        """懒加载 Pix2Text 模型，只有在首次使用时才加载"""
        if self.p2t is None:
            # 导入时才载入 Pix2Text 库
            from pix2text import Pix2Text
            logging.info("正在加载 Pix2Text 模型...")
            self.p2t = Pix2Text.from_config(**CONFIG["pix2text"])
            logging.info("Pix2Text 模型加载完成")
        return self.p2t

    @rumps.clicked("Text_Formula OCR")
    def recognize_mixed(self, _):
        # Identify mixed image
        image = ImageGrab.grabclipboard()
        try:
            p2t = self._get_p2t()
            only_text = p2t.recognize_text_formula(
                image, resized_shape=TEXT_FORMULA_RESIZED_SHAPE, return_text=True
            )  # 也可以使用 `p2t(img_fp, resized_shape=608)` 获得相同的结果
            SUCCESS_NT_FORM["message"] = only_text
            pyperclip.copy(only_text)
            rumps.notification(**SUCCESS_NT_FORM)
            # 释放内存
            gc.collect()
        except Exception as e:
            ERROR_NT_FORM["message"] = str(e)
            rumps.notification(**ERROR_NT_FORM)

    @rumps.clicked("Formula OCR")
    def recognize_formula(self, _):
        # Only recognize formula
        image = ImageGrab.grabclipboard()
        try:
            formula_str = self._get_p2t().recognize_formula(image)
            pyperclip.copy(f"$$\n{formula_str}\n$$")
            SUCCESS_NT_FORM["message"] = formula_str
            rumps.notification(**SUCCESS_NT_FORM)
        except Exception as e:
            ERROR_NT_FORM["message"] = str(e)
            rumps.notification(**ERROR_NT_FORM)

    @rumps.clicked("Text OCR")
    def recognize_text(self, _):
        # Only recognize formula
        image = ImageGrab.grabclipboard()
        try:
            text_str = self._get_p2t().recognize_text(image)
            pyperclip.copy(text_str)
            SUCCESS_NT_FORM["message"] = text_str
            rumps.notification(**SUCCESS_NT_FORM)
        except Exception as e:
            ERROR_NT_FORM["message"] = str(e)
            rumps.notification(**ERROR_NT_FORM)

    @rumps.clicked("Page OCR")
    def recognize_page(self, _):
        # Identify page image
        image = ImageGrab.grabclipboard()
        suffix = list(string.ascii_letters)
        random.shuffle(suffix)
        suffix = "".join(suffix[:6])
        fp_suffix = f"{time.time()}-{suffix}"
        out_debug_dir = OUTPUT_DEBUG_DIR / f"out-debug-{fp_suffix}"
        output_dir = OUTPUT_MD_ROOT_DIR / f"output-{fp_suffix}"
        try:
            page = self._get_p2t().recognize_page(
                image, resized_shape=PAGE_RESIZED_SHAPE, save_debug_res=out_debug_dir
            )
            only_text = page.to_markdown(output_dir)
            SUCCESS_NT_FORM["message"] = (
                f"saved to {output_dir.absolute()}!\n" + only_text
            )
            pyperclip.copy(only_text)
            rumps.notification(**SUCCESS_NT_FORM)
        except Exception as e:
            ERROR_NT_FORM["message"] = str(e)
            rumps.notification(**ERROR_NT_FORM)

    @rumps.notifications
    def notification_center(self, info):
        pass

    @rumps.clicked("On / Off")
    def onoff(self, _):
        mixed_ocr_button = self.menu["Text_Formula OCR"]
        if mixed_ocr_button.callback is None:
            mixed_ocr_button.set_callback(self.recognize_mixed)
        else:
            mixed_ocr_button.set_callback(None)
        formula_ocr_button = self.menu["Formula OCR"]
        if formula_ocr_button.callback is None:
            formula_ocr_button.set_callback(self.recognize_formula)
        else:
            formula_ocr_button.set_callback(None)
        formula_ocr_button = self.menu["Text OCR"]
        if formula_ocr_button.callback is None:
            formula_ocr_button.set_callback(self.recognize_text)
        else:
            formula_ocr_button.set_callback(None)
        page_ocr_button = self.menu["Page OCR"]
        if page_ocr_button.callback is None:
            page_ocr_button.set_callback(self.recognize_page)
        else:
            page_ocr_button.set_callback(None)

    def on_hotkey_pressed(self):
        """当热键被按下时执行的操作"""
        # 创建临时文件用于保存截图
        temp_file = tempfile.mktemp(suffix=".png")

        try:
            # 使用 macOS 的截图工具进行截图并保存到临时文件
            subprocess.run(["screencapture", "-i", "-s", temp_file], check=True)

            # 检查文件是否存在且不为空（确保用户确实截图了）
            if os.path.exists(temp_file) and os.path.getsize(temp_file) > 0:
                # 加载截图
                image = Image.open(temp_file)

                # 调用公式识别功能
                try:
                    formula_str = self._get_p2t().recognize_formula(image)
                    pyperclip.copy(f"$$\n{formula_str}\n$$")
                    SUCCESS_NT_FORM["message"] = formula_str
                    rumps.notification(**SUCCESS_NT_FORM)
                except Exception as e:
                    ERROR_NT_FORM["message"] = str(e)
                    rumps.notification(**ERROR_NT_FORM)
            else:
                # 用户取消了截图
                pass

        except Exception as e:
            ERROR_NT_FORM["message"] = f"截图失败: {str(e)}"
            rumps.notification(**ERROR_NT_FORM)
        finally:
            # 清理临时文件
            if os.path.exists(temp_file):
                os.remove(temp_file)
            # 释放内存
            gc.collect()

    def start_keyboard_listener(self):
        """启动键盘监听器"""
        # 创建一个组合键监听器，监听 cmd+shift+a
        self.hotkey_listener = keyboard.GlobalHotKeys(
            {"<cmd>+<shift>+a": self.on_hotkey_pressed}
        )
        self.hotkey_listener.start()


if __name__ == "__main__":
    Pix2TextApplication(name="").run()
