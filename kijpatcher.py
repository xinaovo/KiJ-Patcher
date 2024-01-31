"""
    KIJ-Patcher. Patch KiCad generated gerber file to complies with JLC rules.

    Copyright (C) 2024 Xina.
    Copyright (C) 2023 ngHackerX86.

    This is a free software released under GNU GPLv2. See LICENSE for more information.
    This software should be used for academic research purpose ONLY and it is NOT FOR COMMERCIAL PURPOSES.

    We are not affiliated, associated, authorized, endorsed by, or in any way officially connected with
    Shenzhen JLC Technology Group Co., Ltd and its subsidiaries.

    JLC and EasyEDA are registered trademarks of Shenzhen JLC Technology Group Co., Ltd and its subsidiaries.
    We makes contextual use of the trademarks of Shenzhen JLC Technology Group Co., Ltd and its subsidiaries
    to indicate the function of the program.
"""

import os
import shutil
import zipfile
import datetime

# 下单用的文件的位置
path_final = "patched"

# 用于检查文件是否为Gerber文件以判断是否进行替换操作
file_filter = ('.gbl','.gbs','.gbp','.gbo','.gm1','gm13',
               '.gtl','.gts','.gtp','.gto','.drl','.G1',
               '.G2','.gko')

#EasyEDA current version
jlcEditorVersion = "6.5.39"

#Generate header with current time
jlcHeader="""G04 Layer: BottomLayer*
G04 EasyEDA v{}, {}*
G04 Gerber Generator version 0.2*
G04 Scale: 100 percent, Rotated: No, Reflected: No *
G04 Dimensions in inches *
G04 leading zeros omitted , absolute positions ,3 integer and 6 decimal *""".format(jlcEditorVersion, datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

jlc_order_tips_txt="""如何进行PCB下单

请查看：
https://docs.lceda.cn/cn/PCB/Order-PCB"""

# 两张对应表，分别根据结尾和文件名来判断该给什么生成的文件什么名称
replace_list_end = [('.gbl',"Gerber_BottomLayer.GBL"),
                    ('.gko',"Gerber_BoardOutlineLayer.GKO"),
                    ('.gbp',"Gerber_BottomPasteMaskLayer.GBP"),
                    ('.gbo',"Gerber_BottomSilkscreenLayer.GBO"),
                    ('.gbs',"Gerber_BottomSolderMaskLayer.GBS"),
                    ('.gtl',"Gerber_TopLayer.GTL"),
                    ('.gtp',"Gerber_TopPasteMaskLayer.GTP"),
                    ('.gto',"Gerber_TopSilkscreenLayer.GTO"),
                    ('.gts',"Gerber_TopSolderMaskLayer.GTS"),
                    ('.gd1',"Drill_Through.GD1"),
                    ('.gm1',"Gerber_MechanicalLayer1.GM1"),
                    ('.gm13',"Gerber_MechanicalLayer13.GM13")]

replace_list_contain = [('_PCB-PTH', "Drill_PTH_Through.DRL"),
                        ('_PCB-NPTH', "Drill_NPTH_Through.DRL"),
                        ('-PTH', "Drill_PTH_Through.DRL"),
                        ('-NPTH', "Drill_NPTH_Through.DRL"),
                        ('_PCB-In1_Cu', "Gerber_InnerLayer1.G1"),
                        ('_PCB-In2_Cu', "Gerber_InnerLayer2.G2"),
                        ('_PCB-Edge_Cuts', "Gerber_BoardOutlineLayer.GKO")]

def zipFolder(folder_path, output_path):
    """
    压缩指定路径下的文件夹
    :param folder_path: 要压缩的文件夹路径
    :param output_path: 压缩文件的输出路径
    """
    with zipfile.ZipFile(output_path, "w", zipfile.ZIP_DEFLATED) as zip:
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                file_path = os.path.join(root, file)
                zip.write(file_path, os.path.relpath(file_path, folder_path))

# 读取Gerber文件和钻孔文件，修改名称并给Gerber文件内容添加识别头后写入到输出文件夹
def patchSingleFile(filename, path_out):
    # 按行读取文件内容
    lines = open(filename).readlines()

    # 检查文件类型并给新文件取好相应的名称，写入识别头和原来的文件内容
    hit_flag = 0

    for replace_couple in replace_list_end:
        if filename.endswith(replace_couple[0]):
            file_new = open(path_out + '/' + replace_couple[1], 'w')
            hit_flag = 1
            break

    if hit_flag == 0:
        for replace_couple in replace_list_contain:
            if filename.find(replace_couple[0]) != -1:
                file_new = open(path_out + '/' + replace_couple[1], 'w')
                hit_flag = 1
                break

    if hit_flag == 1:
        hit_flag = 0

        file_new.write(jlcHeader)

        for line in lines:
            file_new.write(line)

        file_new.close()

def pathInit(path_out):
    # 检查下目录是否存在，没有就创建
    folder_out = os.path.exists(path_out)
    if not folder_out:
        print("Directory %s not found, creating now..." % path_out)
        os.makedirs(path_out)
    else:
        print("Directory \"%s\" exists. Skipping..." % path_out)

    # 清空目录
    print("Directory is not empty. Deleting everything...")
    for files in os.listdir(path_out):
        path = os.path.join(path_out, files)
        try:
            shutil.rmtree(path)
        except OSError:
            os.remove(path)

if __name__ == "__main__":
    print(jlcHeader)
    gerberFilesDir = input("Enter the Gerber output directory: ")
    os.chdir(gerberFilesDir)
    pathInit("patched")

    file_count = 0
    fileList = os.listdir(gerberFilesDir)

    # 遍历out目录下的文件，识别类型并进行相应的处理
    for p in fileList:
        if(os.path.isfile(os.path.join(gerberFilesDir, p))):
            if(p.endswith(file_filter)):
                print("Gerber file %s found, patching..." % p)
                patchSingleFile(os.path.join(gerberFilesDir, p), os.path.join(os.getcwd(), path_final))
                file_count += 1

    with open(gerberFilesDir +"/" + path_final + "/PCB下单必读.txt", "w") as tipstxt:
        tipstxt.write(jlc_order_tips_txt)
    
    timestamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S')

    outputFileName = "PATCHED"  + '-' + timestamp + ".zip"

    zipFolder(path_final , outputFileName)
    print("Patched Gerber files saved as", outputFileName)