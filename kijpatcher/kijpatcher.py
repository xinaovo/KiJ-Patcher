"""
    KIJ-Patcher. Patch KiCad-generated gerber file to complies with JLC rules.

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

PROGRAM_VERSION_STRING = "1.0.0"
# Output path of patched files
PATCHED_FILES_TEMPORARY_DIRECTORY_NAME = "patched"

# Gerber files filter
FILE_FILTERS = ('.gbl','.gbs','.gbp','.gbo','.gm1','gm13',
               '.gtl','.gts','.gtp','.gto','.drl','.g1',
               '.g2','g3','g4','.gko')

# EasyEDA version string
EASYEDA_VERSION_STRING_STD = "EasyEDA v6.5.50"
EASYEDA_VERSION_STRING_PRO = "EasyEDA Pro v2.2.40.3"

# Order tips text
JLC_ORDER_TIPS_TEXT="""如何进行PCB下单

请查看：
https://docs.lceda.cn/cn/PCB/Order-PCB"""

RANDOM_ID_LENGTH = 32

# Replace list of file suffix and file name.
gerberReplaceListFileSuffix = [('.gbl',"Gerber_BottomLayer.GBL", "BottomLayer"),
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

gerberReplaceListFileName = [ ('-In1_Cu', "Gerber_InnerLayer1.G1", "InnerLayer1"),
                        ('-In2_Cu', "Gerber_InnerLayer2.G2", "InnerLayer2"),
                        ('-In3_Cu', "Gerber_InnerLayer3.G3", "InnerLayer3"),
                        ('-In4_Cu', "Gerber_InnerLayer4.G2", "InnerLayer4"),
                        ('-Edge_Cuts', "Gerber_BoardOutlineLayer.GKO", "BoardOutlineLayer")]

#drillReplaceListFileSuffix = []

drillReplaceListFileName = [('_PCB-PTH', "Drill_PTH_Through.DRL", "PTH_Through"),
                        ('_PCB-NPTH', "Drill_NPTH_Through.DRL", "NPTH_Through"),
                        ('-PTH', "Drill_PTH_Through.DRL", " PTH_Through"),
                        ('-NPTH', "Drill_NPTH_Through.DRL", "NPTH_Through")]

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
G04 {}, {}*
G04 {},{},10*
G04 Gerber Generator version 0.2*
G04 Scale: 100 percent, Rotated: No, Reflected: No *
G04 Dimensions in inches *
G04 leading zeros omitted , absolute positions ,3 integer and 6 decimal *""".format(layer,
                                                                                     versionString, timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                                                                                       id1, id2)
    return gerberHeader

def getDrillHeader(layer, versionString, timestamp, id1, id2):
    drillHeader="""M48
METRIC,LZ,000.000
;FILE_FORMAT=3:3
;TYPE=NON_PLATED
;Layer: {}
;{}, {}
;{},{},10
;Gerber Generator version 0.2
""".format(layer,
            versionString, timestamp.strftime("%Y-%m-%d %H:%M:%S"),
            id1, id2)
    return drillHeader

# Read Gerber and drill file, add JLC-specific header and write it to output dir with corresponding name.
def patchSingleFile(filename, outputPath, easyedaVersion, id1, id2):
    # Read file by line
    lines = open(filename).readlines()

    # Rename file with name corresponding to the filetype and add JLC specific header
    flag = 0
    isGerber = False
    currentLayer = ""

    for fileSuffixPair in gerberReplaceListFileSuffix:
        if filename.endswith(fileSuffixPair[0]):
            newFile = open(outputPath + '/' + fileSuffixPair[1], 'w')
            currentLayer = fileSuffixPair[2]
            flag = 1
            isGerber = True
            break

    if flag == 0:
        for fileNamePair in gerberReplaceListFileName:
            if filename.find(fileNamePair[0]) != -1:
                newFile = open(outputPath + '/' + fileNamePair[1], 'w')
                currentLayer = fileNamePair[2]
                flag = 1
                isGerber = True
                break

    if flag == 0:
        for fileNamePair in drillReplaceListFileName:
            if filename.find(fileNamePair[0]) != -1:
                newFile = open(outputPath + '/' + fileNamePair[1], 'w')
                currentLayer = fileNamePair[2]
                flag = 1
                isGerber = False
                break

    if flag == 1:
        flag = 0

        # If the corresponding value of board layer identifier is missing, use default value "BottomLayer"
        if len(currentLayer) == 0:
            currentLayer = "BottomLayer"

        if(isGerber):
            newFile.write(getGerberHeader(currentLayer,easyedaVersion, datetime.datetime.now(), id1, id2))
        else:
            newFile.write(getDrillHeader(currentLayer,easyedaVersion, datetime.datetime.now(), id1, id2))

        for line in lines:
            newFile.write(line)

        newFile.close()

def pathInit(outputPath):
    # Create output directory if it doesn't exist
    outputFolder = os.path.exists(outputPath)
    if not outputFolder:
        print("Directory {} not found, creating now...".format(outputPath))
        os.makedirs(outputPath)
    else: # Empty the directory
        print("Deleting everything in directory {}...".format(outputPath))
        for files in os.listdir(outputPath):
            path = os.path.join(outputPath, files)
            try:
                shutil.rmtree(path)
            except OSError:
              os.remove(path)

# Program Entry
#if __name__ == "__main__":
def main():
    
        print("""KiJ Patcher {}
Copyright (c) 2024-2025 Xina.
Copyright (c) 2023 ngHackerX86.
This is a free software released under GNU GPLv2. See LICENSE for more information.
""".format(PROGRAM_VERSION_STRING))
    
        # Command line options parser init.
        parser = argparse.ArgumentParser(prog="KiJ Patcher",
                                     usage="kijpatcher -i <input> -o <output>",
                                     description="Patch KiCad-generated gerber file to complies with JLC rules.",
                                     )
        parser.add_argument("-i", "--input-folder", help="PATH to gerber files directory")
        parser.add_argument("-o", "--output-file", help="PATH to output file, if FULL path is given. Otherwise, it specifies the output file name.")
        parser.add_argument("-t", "--version-string-type", required=False, default="std", choices=["std", "pro"], help="Specify EasyEDA version type string in Gerber header")
        parser.add_argument('positional_input', nargs='?', help='Lazy mode, specify gerbers files directory only')
        args = parser.parse_args()

        if args.input_folder:
            gerberFilesDir = args.input_folder
        elif args.positional_input:
            gerberFilesDir = args.positional_input
        else:
            print("ERROR: No gerber files directory specified.")
            exit(1)
        os.chdir(gerberFilesDir)
        pathInit(PATCHED_FILES_TEMPORARY_DIRECTORY_NAME)

        fileCount = 0
        fileList = os.listdir(gerberFilesDir)

        # Iterate files in the gerber dir and patch them/.
        randomID1 = generateRandomString(RANDOM_ID_LENGTH)
        randomID2 = generateRandomString(RANDOM_ID_LENGTH)

        easyedaVersionString = ""
        if(args.version_string_type == "pro"):
            easyedaVersionString = EASYEDA_VERSION_STRING_PRO
        else:
            easyedaVersionString = EASYEDA_VERSION_STRING_STD

        for p in fileList:
            if(os.path.isfile(os.path.join(gerberFilesDir, p))):
                if(p.endswith(FILE_FILTERS)):
                    print("Gerber/Drill file %s found, patching..." % p)
                    patchSingleFile(os.path.join(gerberFilesDir, p), os.path.join(os.getcwd(), PATCHED_FILES_TEMPORARY_DIRECTORY_NAME), easyedaVersionString, randomID1, randomID2)
                    fileCount += 1

        with open(os.path.join(os.getcwd(), PATCHED_FILES_TEMPORARY_DIRECTORY_NAME) + "/PCB下单必读.txt", "wb") as tipstxt:
            tipstxt.write(JLC_ORDER_TIPS_TEXT.encode("utf-8"))
    
        timestamp = datetime.datetime.now()

        projectName = ""
        for file in fileList:
            if(os.path.isfile(os.path.join(gerberFilesDir, file))):
                if(file.endswith("-Edge_Cuts.gm1")):
                 projectName = file[0:file.find("-Edge_Cuts.gm1", 0)]
    
        outputFilePath = ""
        if args.output_file == None:
            outputFilePath = gerberFilesDir + "/" + "Gerber_{}_{}.zip".format(projectName, timestamp.strftime('%Y-%m-%d'))
        else:
            outputFilePath = args.output_file

        zipFolder(PATCHED_FILES_TEMPORARY_DIRECTORY_NAME , outputFilePath)
        print("Patched Gerber files saved as", outputFilePath)
        print("Cleaning up temporary files and directory...")
        pathInit(os.path.join(os.getcwd(), PATCHED_FILES_TEMPORARY_DIRECTORY_NAME))
        os.removedirs(os.path.join(os.getcwd(), PATCHED_FILES_TEMPORARY_DIRECTORY_NAME))
