import os
import random
from PIL import Image, ImageDraw, ImageFont

# -------------------------------
# 配置参数
# -------------------------------
IMAGE_SIZE = (800, 600)           # 图片大小
BACKGROUND_GRAY = None            # None 表示随机灰度背景 (0-255)，也可设为 128
NUM_TEXTS = 3                     # 添加的文字数量
FONT_PATH = "./baige.ttf"      # Mac
MIN_FONT_SIZE = 20
MAX_FONT_SIZE = 60
TEXT_CONTENTS = ["Hello", "World", "Python", "AI", "Clip", "Stable", "Diffusion", "Text"]
OUTPUT_DIR = "output"
MASK_IMAGE_NAME = "mask.png"
IMAGE_PATH = "/home/sxm/flux-workspace/FluxText/assets/hint_imgs.jpg"

# -------------------------------
# 创建输出目录
# -------------------------------
os.makedirs(OUTPUT_DIR, exist_ok=True)


from PIL import Image

def get_image_size(image_path):
    """
    获取指定路径下图片的尺寸（宽度, 高度）。
    
    :param image_path: 图片文件的路径。
    :return: 一个包含图片宽度和高度的元组 (width, height)。
    """
    with Image.open(image_path) as img:
        return img.size  # 返回的是 (宽度, 高度)
    
def random_gray():
    """生成随机灰度值作为背景"""
    return 255

def random_text_color(bg_gray):
    """根据背景亮度选择黑或白文字"""
    return 255 if bg_gray < 150 else 0  # 返回 0（黑）或 255（白）

def create_mask(boxes, image_size=IMAGE_SIZE):
    """
    根据bounding boxes创建mask图像。
    
    :param boxes: list of dict, 每个dict包含'box': (left, top, right, bottom)
    :param image_size: tuple, 目标图像大小
    :return: None, 保存生成的mask图像到文件
    """
    # 创建一个全黑（0值）图像作为背景
    mask_image = Image.new('L', image_size, 0)
    draw = ImageDraw.Draw(mask_image)

    for box_info in boxes:
        box = box_info['box']
        # 在mask图上绘制白色矩形
        draw.rectangle(box, fill=None, outline=255, width=2)  # 使用白色边框表示bbox

    # 保存mask图像
    output_path = os.path.join(OUTPUT_DIR, MASK_IMAGE_NAME)
    mask_image.save(output_path)
    print(f"Mask图像已保存: {output_path}")

def create_filled_mask(boxes, image_size=IMAGE_SIZE):
    """
    根据bounding boxes创建内部填充白色的mask图像。
    
    :param boxes: list of dict, 每个dict包含'box': (left, top, right, bottom)
    :param image_size: tuple, 目标图像大小
    :return: None, 保存生成的mask图像到文件
    """
    # 创建一个全黑（0值）图像作为背景
    mask_image = Image.new('L', image_size, 0)
    draw = ImageDraw.Draw(mask_image)

    for box_info in boxes:
        box = box_info['box']
        # 在mask图上绘制白色填充矩形
        draw.rectangle(box, fill=255, outline=None)  # 使用fill=255来填充矩形

    # 确保输出目录存在
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    # 保存mask图像
    output_path = os.path.join(OUTPUT_DIR, MASK_IMAGE_NAME)
    mask_image.save(output_path)
    print(f"Mask图像已保存: {output_path}")

def draw_text_and_get_bbox(draw, text, position, font, text_color):
    """
    在指定位置绘制文本，并返回文本的外接矩形框（左、上、右、下）。
    
    :param draw: ImageDraw对象，用于绘图。
    :param text: 要绘制的文本内容。
    :param position: 文本位置 (x, y)，文本的左上角坐标。
    :param font: 使用的字体。
    :param text_color: 文本颜色。
    :return: 文本的外接矩形框 (left, top, right, bottom)。
    """
    # 获取文字尺寸
    try:
        bbox = font.getbbox(text)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
    except AttributeError:
        # 对于不支持getbbox的PIL版本，使用getsize方法作为后备
        text_width, text_height = font.getsize(text)

    # 计算文本位置
    x, y = position

    # 绘制文本到draw对象
    draw.text((x, y), text, font=font, fill=text_color)

    # 返回文本的外接矩形框
    return (x, y, x + text_width, y + text_height)

def draw_rotated_text(draw, text, position, angle, font, text_color):
    """绘制旋转文字并返回其外接矩形框（左、上、右、下）"""
    # 获取文字尺寸
    try:
        bbox = font.getbbox(text)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
    except:
        # fallback
        text_width, text_height = font.getsize(text)

    # 创建透明图层用于旋转
    dummy = Image.new('RGBA', (text_width + 10, text_height + 10), (0, 0, 0, 0))
    d = ImageDraw.Draw(dummy)
    d.text((5, 5), text, fill=(255, 255, 255, 255) if text_color == 255 else (0, 0, 0, 255), font=font)

    # 旋转
    rotated = dummy.rotate(angle, expand=True)

    # 计算粘贴位置（以中心为旋转中心）
    cx, cy = position
    paste_w, paste_h = rotated.size
    left = cx - paste_w // 2
    top = cy - paste_h // 2

    # 粘贴到主图（灰度图）
    draw._image.paste(rotated, (left, top), rotated)

    # 返回旋转后图像的外接矩形（保守估计）
    return (left, top, left + paste_w, top + paste_h)

def main():
    # 设置背景灰度
    if BACKGROUND_GRAY is None:
        bg_gray = random_gray()
    else:
        bg_gray = BACKGROUND_GRAY

    # 创建灰度图像 (模式 'L': 8-bit pixels, black and white)
    image = Image.new('L', IMAGE_SIZE, bg_gray)
    draw = ImageDraw.Draw(image)
    draw._image = image  # 用于 paste 操作

    results = []

    for _ in range(NUM_TEXTS):
        # 随机文字
        text = random.choice(TEXT_CONTENTS)

        # 随机字体大小
        font_size = random.randint(MIN_FONT_SIZE, MAX_FONT_SIZE)
        try:
            font = ImageFont.truetype(FONT_PATH, font_size)
        except IOError:
            print(f"警告: 字体 {FONT_PATH} 未找到，使用默认字体（可能不支持复杂文本）")
            font = ImageFont.load_default()

        # 获取文字尺寸以确定位置
        try:
            bbox = font.getbbox(text)
            w = bbox[2] - bbox[0]
            h = bbox[3] - bbox[1]
        except:
            w, h = font.getsize(text)

        # 随机位置（防止越界）
        x = random.randint(w // 2, IMAGE_SIZE[0] - w // 2)
        y = random.randint(h // 2, IMAGE_SIZE[1] - h // 2)

        # 随机旋转角度
        # angle = random.randint(0, 360)
        angle = 0

        # 文字颜色：黑(0) 或 白(255)
        text_color = random_text_color(bg_gray)

        # 绘制并获取框
        # box = draw_rotated_text(draw, text, (x, y), angle, font, text_color)
        box = draw_text_and_get_bbox(draw, text, (x, y), font, text_color)

        # 保存信息
        results.append({
            'text': text,
            'box': box,        # (left, top, right, bottom)
            'color': text_color,  # 0 或 255
            'angle': angle
        })

        create_filled_mask(results, image_size=IMAGE_SIZE)

        print(f"添加文字: '{text}' 在 {box}, 颜色: {'白' if text_color == 255 else '黑'}, 角度: {angle}°")

    # 保存灰度图
    output_image_path = os.path.join(OUTPUT_DIR, "grayscale_with_text.png")
    image.save(output_image_path)
    print(f"\n灰度图片已保存: {output_image_path}")

    # 保存文字和框信息
    output_txt_path = os.path.join(OUTPUT_DIR, "text_boxes_grayscale.txt")
    with open(output_txt_path, 'w') as f:
        for item in results:
            color_str = "white" if item['color'] == 255 else "black"
            f.write(f"文字: {item['text']}, 框: {item['box']}, 颜色: {color_str}, 角度: {item['angle']}°\n")
    print(f"文字信息已保存: {output_txt_path}")

    # 可选：显示图像（需要 GUI）
    # image.show()

if __name__ == "__main__":
    if len(IMAGE_PATH) == 0:
        IMAGE_SIZE = get_image_size(IMAGE_PATH)
    main()