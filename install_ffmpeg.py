"""
FFmpeg自动安装器
FFmpeg Auto Installer for Windows

自动下载并配置FFmpeg，无需手动安装
"""
import os
import sys
import zipfile
import urllib.request
from pathlib import Path


def install_ffmpeg():
    """自动安装FFmpeg到项目目录"""
    
    # 检查是否已安装
    if check_ffmpeg():
        print("✅ FFmpeg already installed and working!")
        return True
    
    print("📥 Installing FFmpeg automatically...")
    print("   This may take a few minutes...\n")
    
    # 项目根目录
    base_dir = Path(__file__).parent.resolve()
    ffmpeg_dir = base_dir / "ffmpeg"
    ffmpeg_dir.mkdir(exist_ok=True)
    
    # 下载地址
    download_url = "https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip"
    zip_path = ffmpeg_dir / "ffmpeg.zip"
    
    try:
        # 下载
        print("⬇️  Downloading FFmpeg...")
        urllib.request.urlretrieve(download_url, zip_path)
        print("✅ Download complete!\n")
        
        # 解压
        print("📦 Extracting...")
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(ffmpeg_dir)
        print("✅ Extraction complete!\n")
        
        # 找到解压后的文件夹
        extracted_folder = None
        for item in ffmpeg_dir.iterdir():
            if item.is_dir() and item.name.startswith('ffmpeg-'):
                extracted_folder = item
                break
        
        if not extracted_folder:
            print("❌ Could not find extracted FFmpeg folder")
            return False
        
        # 创建bin目录的符号链接或复制文件
        bin_source = extracted_folder / "bin"
        bin_target = ffmpeg_dir / "bin"
        
        if bin_target.exists():
            import shutil
            shutil.rmtree(bin_target)
        
        # 复制bin目录
        import shutil
        shutil.copytree(bin_source, bin_target)
        
        # 清理
        zip_path.unlink()
        shutil.rmtree(extracted_folder)
        
        print("✅ FFmpeg installed successfully!")
        print(f"📁 Location: {bin_target}\n")
        
        return True
        
    except Exception as e:
        print(f"❌ Installation failed: {e}")
        return False


def check_ffmpeg():
    """检查FFmpeg是否可用"""
    import subprocess
    try:
        # 先检查环境变量
        subprocess.run(['ffmpeg', '-version'], capture_output=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        # 检查项目本地目录
        base_dir = Path(__file__).parent.resolve()
        local_ffmpeg = base_dir / "ffmpeg" / "bin" / "ffmpeg.exe"
        if local_ffmpeg.exists():
            return True
        return False


def get_ffmpeg_path():
    """获取FFmpeg可执行文件路径"""
    import shutil
    
    # 先检查系统PATH
    ffmpeg_exe = shutil.which('ffmpeg')
    if ffmpeg_exe:
        return Path(ffmpeg_exe).parent
    
    # 检查项目本地目录
    base_dir = Path(__file__).parent.resolve()
    local_bin = base_dir / "ffmpeg" / "bin"
    if (local_bin / "ffmpeg.exe").exists():
        return local_bin
    
    return None


def setup_ffmpeg_path():
    """设置FFmpeg路径到环境变量"""
    ffmpeg_bin = get_ffmpeg_path()
    if ffmpeg_bin:
        os.environ['PATH'] = str(ffmpeg_bin) + os.pathsep + os.environ.get('PATH', '')
        return True
    return False


if __name__ == "__main__":
    if install_ffmpeg():
        print("\n🎉 FFmpeg is ready to use!")
        print("   You can now run YouTube learning commands.")
    else:
        print("\n❌ FFmpeg installation failed.")
        print("   Please install manually from: https://www.gyan.dev/ffmpeg/builds/")
        sys.exit(1)
