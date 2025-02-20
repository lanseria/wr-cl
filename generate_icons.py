"""Generate platform-specific icons from a source image."""
import sys
import subprocess
from pathlib import Path


def generate_windows_icon(source_image, output_path):
    """Generate Windows .ico file."""
    try:
        from PIL import Image
        img = Image.open(source_image)
        img.save(output_path, format='ICO', sizes=[
                 (256, 256), (128, 128), (64, 64), (32, 32), (16, 16)])
        print(f"Generated Windows icon: {output_path}")
    except ImportError:
        print("Please install Pillow: pip install Pillow")
        sys.exit(1)


def generate_macos_icon(source_image, output_path):
    """Generate macOS .icns file."""
    try:
        # 确保目录存在
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # 使用 sips 和 iconutil（macOS 专用工具）
        if sys.platform == 'darwin':
            iconset_path = output_path.parent / 'icon.iconset'
            iconset_path.mkdir(exist_ok=True)

            sizes = [16, 32, 64, 128, 256, 512]
            for size in sizes:
                subprocess.run([
                    'sips',
                    '-z', str(size), str(size),
                    source_image,
                    '--out', str(iconset_path / f'icon_{size}x{size}.png')
                ], check=True)
                # 为 Retina 显示器创建 2x 版本
                subprocess.run([
                    'sips',
                    '-z', str(size*2), str(size*2),
                    source_image,
                    '--out', str(iconset_path / f'icon_{size}x{size}@2x.png')
                ], check=True)

            # 转换为 .icns
            subprocess.run([
                'iconutil',
                '-c', 'icns',
                str(iconset_path),
                '-o', str(output_path)
            ], check=True)

            # 清理临时文件
            import shutil
            shutil.rmtree(iconset_path)

            print(f"Generated macOS icon: {output_path}")
        else:
            print("macOS icon generation is only supported on macOS")
    except Exception as e:
        print(f"Error generating macOS icon: {e}")
        sys.exit(1)


def main():
    """Main entry point."""
    # 获取项目根目录
    root_dir = Path(__file__).parent.parent
    icons_dir = root_dir / 'resources' / 'icons'
    icons_dir.mkdir(parents=True, exist_ok=True)

    # 源图像（应该是一个高分辨率的 PNG 文件）
    source_image = root_dir / 'resources' / 'source_icon.png'

    if not source_image.exists():
        print(f"Source image not found: {source_image}")
        sys.exit(1)

    # 生成 Windows 图标
    generate_windows_icon(source_image, icons_dir / 'icon.ico')

    # 在 macOS 上生成 macOS 图标
    if sys.platform == 'darwin':
        generate_macos_icon(source_image, icons_dir / 'icon.icns')


if __name__ == "__main__":
    main()
