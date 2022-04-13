# 导入相关库
import os
import glob
import shutil
from gooey import Gooey, GooeyParser

# 定义一个文件字典，不同的文件类型，属于不同的文件夹，一共9个大类。
file_dict = {
    '图片': ['jpg', 'png', 'gif', 'webp'],
    '视频': ['rmvb', 'mp4', 'avi', 'mkv', 'flv'],
    "音频": ['cd', 'wave', 'aiff', 'mpeg', 'mp3', 'mpeg-4'],
    '文档': ['xls', 'xlsx', 'csv', 'doc', 'docx', 'ppt', 'pptx', 'pdf', 'txt'],
    '压缩文件': ['7z', 'ace', 'bz', 'jar', 'rar', 'tar', 'zip', 'gz'],
    '常用格式': ['json', 'xml', 'md', 'ximd'],
    '程序脚本': ['py', 'java', 'html', 'sql', 'r', 'css', 'cpp', 'c', 'sas', 'js', 'go'],
    '可执行程序': ['exe', 'bat', 'lnk', 'sys', 'com'],
    '字体文件': ['eot', 'otf', 'fon', 'font', 'ttf', 'ttc', 'woff', 'woff2']
}


# 定义一个函数，传入每个文件对应的后缀。判断文件是否存在于字典file_dict中；
# 如果存在，返回对应的文件夹名；如果不存在，将该文件夹命名为"未知分类"；
def func(suffix):
    for name, type_list in file_dict.items():
        if suffix.lower() in type_list:
            return name
    return "未知分类"


@Gooey(encoding='utf-8', program_name="King整理文件小工具-V1.0.1\n\n", language='chinese')
def start():
    parser = GooeyParser()
    parser.add_argument("path", help="请选择要整理的文件路径：", widget="DirChooser")  # 一定要用双引号 不然没有这个属性
    args = parser.parse_args()
    # print(args, flush=True)  # 坑点：flush=True在打包的时候会用到
    return args


if __name__ == '__main__':
    args = start()
    path = args.path

    # 递归获取 "待处理文件路径" 下的所有文件和文件夹。
    for file in glob.glob(f"{path}/**/*", recursive=True):
        # 由于我们是对文件分类，这里需要挑选出文件来。
        if os.path.isfile(file):
            # 由于isfile()函数，获取的是每个文件的全路径。这里再调用basename()函数，直接获取文件名；
            file_name = os.path.basename(file)
            suffix = file_name.split(".")[-1]
            # 判断 "文件名" 是否在字典中。
            name = func(suffix)
            # print(func(suffix))
            # 根据每个文件分类，创建各自对应的文件夹。
            if not os.path.exists(f"{path}\\{name}"):
                os.mkdir(f"{path}\\{name}")
            # 将文件复制到各自对应的文件夹中。
            shutil.copy(file, f"{path}\\{name}")
