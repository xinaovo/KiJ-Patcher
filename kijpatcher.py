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
import argparse

# 下单用的文件的位置
path_final = "patched"

# Gerber files filter
file_filter = ('.gbl','.gbs','.gbp','.gbo','.gm1','gm13',
               '.gtl','.gts','.gtp','.gto','.drl','.G1',
               '.G2','.gko')

# EasyEDA version string
jlcEditorVersion = "6.5.50"

# Generate header with current time
gerberHeader="""G04 Layer: BottomLayer*
G04 EasyEDA v{}, {}*
G04 Gerber Generator version 0.2*
G04 Scale: 100 percent, Rotated: No, Reflected: No *
G04 Dimensions in inches *
G04 leading zeros omitted , absolute positions ,3 integer and 6 decimal *""".format(jlcEditorVersion, datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

jlc_order_tips_txt="""如何进行PCB下单

请查看：
https://docs.lceda.cn/cn/PCB/Order-PCB"""

# Replace list of file suffix and file name.
replace_list_end = [('.gbl',"Gerber_BottomLayer.GBL", "BottomLayer"),
                    ('.gko',"Gerber_BoardOutlineLayer.GKO", "BoardOutlineLayer"),
                    ('.gbp',"Gerber_BottomPasteMaskLayer.GBP",),
                    ('.gbo',"Gerber_BottomSilkscreenLayer.GBO", "BottomSilkscreenLayer"),
                    ('.gbs',"Gerber_BottomSolderMaskLayer.GBS", "BottomSolderMaskLayer"),
                    ('.gtl',"Gerber_TopLayer.GTL", "TopLayer"),
                    ('.gtp',"Gerber_TopPasteMaskLayer.GTP", "TopPasteMaskLayer"),
                    ('.gto',"Gerber_TopSilkscreenLayer.GTO", "TopSilkscreenLayer"),
                    ('.gts',"Gerber_TopSolderMaskLayer.GTS", "TopSolderMaskLayer"),
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
    Compress a folder
    :param folder_path: Path to input folder
    :param output_path: Path to output .zip file.
    """
    with zipfile.ZipFile(output_path, "w", zipfile.ZIP_DEFLATED) as zip:
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                file_path = os.path.join(root, file)
                zip.write(file_path, os.path.relpath(file_path, folder_path))

# Read Gerber and drill file, add JLC-specific header and write it to output dir with corresponding name.
def patchSingleFile(filename, path_out):
    # Read file by line
    lines = open(filename).readlines()

    # Rename file with name corresponding to the filetype and add JLC specific header
    hit_flag = 0
    currentLayer = ""

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

        file_new.write(gerberHeader)

        for line in lines:
            file_new.write(line)

        file_new.close()

def pathInit(path_out):
    # Create output directory if it doesn't exist
    folder_out = os.path.exists(path_out)
    if not folder_out:
        print("Directory %s not found, creating now..." % path_out)
        os.makedirs(path_out)
    else:
        print("Directory \"%s\" exists. Skipping..." % path_out)

    # Empty the directory
    print("Directory is not empty. Deleting everything...")
    for files in os.listdir(path_out):
        path = os.path.join(path_out, files)
        try:
            shutil.rmtree(path)
        except OSError:
            os.remove(path)

# Program Entry
if __name__ == "__main__":
    # Command line options parser init.
    parser = argparse.ArgumentParser(prog="KiJ Patcher",
                                     usage="kijpatcher -i <input> -o <output>",
                                     description="Patch KiCad generated gerber file to complies with JLC rules.",
                                     )
    parser.add_argument("-i", "--input-folder", required=True, help="PATH to gerber files directory")
    parser.add_argument("-o", "--output-file", required=False, help="PATH to output file")
    args = parser.parse_args()

    gerberFilesDir = args.input_folder
    os.chdir(gerberFilesDir)
    pathInit("patched")

    file_count = 0
    fileList = os.listdir(gerberFilesDir)

    # Iterate files in the gerber dir and patch them/.
    for p in fileList:
        if(os.path.isfile(os.path.join(gerberFilesDir, p))):
            if(p.endswith(file_filter)):
                print("Gerber file %s found, patching..." % p)
                patchSingleFile(os.path.join(gerberFilesDir, p), os.path.join(os.getcwd(), path_final))
                file_count += 1

    with open(gerberFilesDir + "/" + path_final + "/PCB下单必读.txt", "w") as tipstxt:
        tipstxt.write(jlc_order_tips_txt)
    
    timestamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S')

    outputFilePath = ""
    if args.output_file == None:
        outputFilePath = args.input_folder + "/" + "Gerber"  + '-' + timestamp + ".zip"
    else:
        outputFilePath = args.output_file

    zipFolder(path_final , outputFilePath)
    print("Patched Gerber files saved as", outputFilePath)