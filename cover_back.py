import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QPushButton, QLabel, QFileDialog, QVBoxLayout, QWidget
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt
from rembg import remove
from PIL import Image, ImageOps, ImageDraw,ImageFilter
import io


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Photo Background Remover")
        self.setGeometry(400, 200, 800, 600)

        # 初始化布局
        layout = QVBoxLayout()

        # 图片展示区域
        self.image_label = QLabel("请选择一张图片")
        self.image_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.image_label)

        # 选择图片按钮
        self.select_button = QPushButton("选择图片")
        self.select_button.clicked.connect(self.select_image)
        layout.addWidget(self.select_button)

        # 去除背景按钮
        self.remove_bg_button = QPushButton("去除背景")
        self.remove_bg_button.clicked.connect(self.remove_background)
        self.remove_bg_button.setEnabled(False)
        layout.addWidget(self.remove_bg_button)

        # 添加背景按钮
        self.set_bg_button = QPushButton("将背景设置为蓝色")
        self.set_bg_button.clicked.connect(self.set_blue_background)
        self.set_bg_button.setEnabled(False)  # 处理完背景后启用
        layout.addWidget(self.set_bg_button)

        # 添加红色背景按钮
        self.set_red_bg_button = QPushButton("将背景设置为红色")
        self.set_red_bg_button.clicked.connect(self.set_red_background)
        self.set_red_bg_button.setEnabled(False)  # 处理完背景后启用
        layout.addWidget(self.set_red_bg_button)

        # 添加调整大小的按钮
        self.one_inch_button = QPushButton('一寸照', self)
        self.one_inch_button.clicked.connect(lambda: self.resize_image((295, 413)))
        layout.addWidget(self.one_inch_button)

        self.two_inch_button = QPushButton('二寸照', self)
        self.two_inch_button.clicked.connect(lambda: self.resize_image((413, 626)))
        layout.addWidget(self.two_inch_button)

        self.three_inch_button = QPushButton('三寸照', self)
        self.three_inch_button.clicked.connect(lambda: self.resize_image((649, 991)))
        layout.addWidget(self.three_inch_button)

        self.six_inch_button = QPushButton('六寸照', self)
        self.six_inch_button.clicked.connect(lambda: self.resize_image((960, 1440)))
        layout.addWidget(self.six_inch_button)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        self.image_path = None
        self.processed_image = None
        self.original_image = None

    # 选择图片
    def select_image(self):
        # 打开文件选择器
        file_dialog = QFileDialog(self)
        file_dialog.setNameFilter("Images (*.png *.jpg *.jpeg)")
        if file_dialog.exec():
            self.image_path = file_dialog.selectedFiles()[0]
            self.original_image = Image.open(self.image_path)
            pixmap = QPixmap(self.image_path)
            self.image_label.setPixmap(pixmap.scaled(295, 413))
            self.remove_bg_button.setEnabled(True)

    # 去除背景
    def remove_background(self):
        if not self.image_path:
            return

        # 读取图片数据并去除背景
        with open(self.image_path, 'rb') as input_file:
            input_data = input_file.read()

        # 修改：增加 post_process_mask 参数，以改善边缘处理
        output_data = remove(input_data, alpha_matting=True,
                             alpha_matting_foreground_threshold=240,
                             alpha_matting_background_threshold=20,
                             alpha_matting_erode_size=38,
                             post_process_mask=True)  # 新增：启用后处理以改善边缘

        # 将处理后的图片保存为 PIL 图像对象
        self.processed_image = Image.open(io.BytesIO(output_data)).convert("RGBA")

        # 修改：增加边缘平滑处理
        self.processed_image = self.smooth_edges(self.processed_image)

        # 显示处理后的图片
        output_path = self.image_path.rsplit(".", 1)[0] + "_no_bg.png"  # 修改：确保输出为PNG格式
        self.processed_image.save(output_path)
        self.original_image = Image.open(output_path)
        pixmap = QPixmap(output_path)
        self.image_label.setPixmap(pixmap.scaled(295, 413))

        # 启用 "将背景设置为蓝色" 按钮
        self.image_path = output_path
        self.set_bg_button.setEnabled(True)
        self.set_red_bg_button.setEnabled(True)

    # 新增：边缘平滑处理函数
    def smooth_edges(self, img):
        # 创建一个只包含 alpha 通道的图像
        alpha = img.split()[-1]
        # 对 alpha 通道应用高斯模糊
        smoothed_alpha = alpha.filter(ImageFilter.GaussianBlur(radius=1))
        # 将平滑处理后的 alpha 通道替换回原图像
        img.putalpha(smoothed_alpha)
        return img

    # 将背景设置为蓝色
    def set_blue_background(self):
        if self.processed_image is None:
            return

        # 创建一个蓝色背景
        blue_background = Image.new("RGBA", self.processed_image.size, (0, 0, 255, 255))  # 蓝色

        # 将处理后的前景图片粘贴到蓝色背景上
        blue_background.paste(self.processed_image, (0, 0), self.processed_image)

        # 保存并显示新图片
        output_path = self.image_path.replace(".png", "_blue_bg.png")
        blue_background.save(output_path)
        self.original_image = Image.open(output_path)
        pixmap = QPixmap(output_path)
        self.image_label.setPixmap(pixmap.scaled(295, 413))

    # 将背景设置为红色
    def set_red_background(self):
        if self.processed_image is None:
            return

        # 创建一个红色背景
        red_background = Image.new("RGBA", self.processed_image.size, (255, 0, 0, 255))  # 红色

        # 将处理后的前景图片粘贴到红色背景上
        red_background.paste(self.processed_image, (0, 0), self.processed_image)

        # 保存并显示新图片
        output_path = self.image_path.replace(".png", "_red_bg.png")
        red_background.save(output_path)
        self.original_image = Image.open(output_path)
        pixmap = QPixmap(output_path)
        self.image_label.setPixmap(pixmap.scaled(295, 413))

    # 调整图片大小
    def resize_image(self, size):
        if self.original_image is None:
            return

        # 调整图片大小，保持原始纵横比
        resized_image = self.original_image.copy()
        resized_image.thumbnail(size, Image.LANCZOS)

        # 创建新的图像，居中放置调整后的图片
        new_image = Image.new("RGB", size, (255, 255, 255))  # 白色背景
        paste_x = (size[0] - resized_image.width) // 2
        paste_y = (size[1] - resized_image.height) // 2
        new_image.paste(resized_image, (paste_x, paste_y))

        # 保存并显示新图片
        output_path = self.image_path.replace(".", f"_{size[0]}x{size[1]}.")
        new_image.save(output_path)
        pixmap = QPixmap(output_path)
        self.image_label.setPixmap(pixmap.scaled(400, 400, Qt.KeepAspectRatio))


if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())
