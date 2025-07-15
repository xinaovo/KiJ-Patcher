"""
    KIJ-Patcher. Patch KiCad generated gerber file to complies with JLC rules.

    Copyright (C) 2024-2025 Xina.
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
import random

PROGRAM_VERSION_STRING = "V0.99 dev"
# Output path of patched files
patchedFilesPath = "patched"

# Gerber files filter
fileFilter = ('.gbl','.gbs','.gbp','.gbo','.gm1','gm13',
               '.gtl','.gts','.gtp','.gto','.drl','.G1',
               '.G2','.gko')

# EasyEDA version string
easyedaVersionString = "6.5.50"

# Order tips text
jlcOrderTipsText="""如何进行PCB下单

请查看：
https://docs.lceda.cn/cn/PCB/Order-PCB"""

RANDOM_ID_LENGTH = 32

# Replace list of file suffix and file name.
replaceListFileSuffix = [('.gbl',"Gerber_BottomLayer.GBL", "BottomLayer"),
                    ('.gko',"Gerber_BoardOutlineLayer.GKO", "BoardOutlineLayer"),
                    ('.gbp',"Gerber_BottomPasteMaskLayer.GBP", "BottomPasteMaskLayer"),
                    ('.gbo',"Gerber_BottomSilkscreenLayer.GBO", "BottomSilkscreenLayer"),
                    ('.gbs',"Gerber_BottomSolderMaskLayer.GBS", "BottomSolderMaskLayer"),
                    ('.gtl',"Gerber_TopLayer.GTL", "TopLayer"),
                    ('.gtp',"Gerber_TopPasteMaskLayer.GTP", "TopPasteMaskLayer"),
                    ('.gto',"Gerber_TopSilkscreenLayer.GTO", "TopSilkscreenLayer"),
                    ('.gts',"Gerber_TopSolderMaskLayer.GTS", "TopSolderMaskLayer"),
                    ('.gd1',"Drill_Through.GD1", ""),
                    ('.gm1',"Gerber_MechanicalLayer1.GM1", ""),
                    ('.gm13',"Gerber_MechanicalLayer13.GM13", "")]

replaceListFileName = [('_PCB-PTH', "Drill_PTH_Through.DRL", ""),
                        ('_PCB-NPTH', "Drill_NPTH_Through.DRL", ""),
                        ('-PTH', "Drill_PTH_Through.DRL", ""),
                        ('-NPTH', "Drill_NPTH_Through.DRL", ""),
                        ('_PCB-In1_Cu', "Gerber_InnerLayer1.G1", "InnerLayer1"),
                        ('_PCB-In2_Cu', "Gerber_InnerLayer2.G2", "InnerLayer2"),
                        ('_PCB-Edge_Cuts', "Gerber_BoardOutlineLayer.GKO", "BoardOutlineLayer")]

def zipFolder(folderPath, outputPath):
    """
    Compress a folder
    :param folderPath: Path to input folder
    :param outputPath: Path to output .zip file.
    """
    with zipfile.ZipFile(outputPath, "w", zipfile.ZIP_DEFLATED) as zip:
        for root, dirs, files in os.walk(folderPath):
            for file in files:
                file_path = os.path.join(root, file)
                zip.write(file_path, os.path.relpath(file_path, folderPath))

def generateRandomString(length: int):
    ALPHABETS = "abcdef0123456789"
    result = ""
    for i in range(length):
        index = random.randint(0, len(ALPHABETS) - 1)
        result += ALPHABETS[index]
    return result

def getGerberHeader(layer, versionString, timestamp, id1, id2):
    gerberHeader="""G04 Layer: {}*
G04 EasyEDA v{}, {}*
G04 {},{},10*
G04 Gerber Generator version 0.2*
G04 Scale: 100 percent, Rotated: No, Reflected: No *
G04 Dimensions in inches *
G04 leading zeros omitted , absolute positions ,3 integer and 6 decimal *""".format(layer,
                                                                                     versionString, timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                                                                                       id1, id2)
    return gerberHeader

# Read Gerber and drill file, add JLC-specific header and write it to output dir with corresponding name.
def patchSingleFile(filename, outputPath, id1, id2):
    # Read file by line
    lines = open(filename).readlines()

    # Rename file with name corresponding to the filetype and add JLC specific header
    flag = 0
    currentLayer = ""

    for fileSuffixPair in replaceListFileSuffix:
        if filename.endswith(fileSuffixPair[0]):
            newFile = open(outputPath + '/' + fileSuffixPair[1], 'w')
            currentLayer = fileSuffixPair[2]
            flag = 1
            break

    if flag == 0:
        for fileNamePair in replaceListFileName:
            if filename.find(fileNamePair[0]) != -1:
                newFile = open(outputPath + '/' + fileNamePair[1], 'w')
                currentLayer = fileNamePair[2]
                flag = 1
                break

    if flag == 1:
        flag = 0

        # If the corresponding value of board layer identifier is missing, use default value "BottomLayer"
        if len(currentLayer) == 0:
            currentLayer = "BottomLayer"

        newFile.write(getGerberHeader(currentLayer,easyedaVersionString, datetime.datetime.now(), id1, id2))

        for line in lines:
            newFile.write(line)

        newFile.close()

def pathInit(outputPath):
    # Create output directory if it doesn't exist
    outputFolder = os.path.exists(outputPath)
    if not outputFolder:
        print("Directory %s not found, creating now..." % outputPath)
        os.makedirs(outputPath)
    else:
        print("Directory \"%s\" exists. Skipping..." % outputPath)

    # Empty the directory
    print("Directory is not empty. Deleting everything...")
    for files in os.listdir(outputPath):
        path = os.path.join(outputPath, files)
        try:
            shutil.rmtree(path)
        except OSError:
            os.remove(path)

# Program Entry
if __name__ == "__main__":
    # Command line options parser init.
    print("""KiJ Patcher {}
Copyright (c) 2024-2025 Xina.
Copyright (c) 2023 ngHackerX86.
This is a free software released under GNU GPLv2. See LICENSE for more information.
""".format(PROGRAM_VERSION_STRING))
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

    fileCount = 0
    fileList = os.listdir(gerberFilesDir)

    # Iterate files in the gerber dir and patch them/.
    randomID1 = generateRandomString(RANDOM_ID_LENGTH)
    randomID2 = generateRandomString(RANDOM_ID_LENGTH)
    for p in fileList:
        if(os.path.isfile(os.path.join(gerberFilesDir, p))):
            if(p.endswith(fileFilter)):
                print("Gerber file %s found, patching..." % p)
                patchSingleFile(os.path.join(gerberFilesDir, p), os.path.join(os.getcwd(), patchedFilesPath), randomID1, randomID2)
                fileCount += 1

    with open(gerberFilesDir + "/" + patchedFilesPath + "/PCB下单必读.txt", "w") as tipstxt:
        tipstxt.write(jlcOrderTipsText)
    
    timestamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S')

    outputFilePath = ""
    if args.output_file == None:
        outputFilePath = args.input_folder + "/" + "Gerber"  + '-' + timestamp + ".zip"
    else:
        outputFilePath = args.output_file

    zipFolder(patchedFilesPath , outputFilePath)
    print("Patched Gerber files saved as", outputFilePath)