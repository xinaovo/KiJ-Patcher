# KiJ-Patcher

Patch KiCad generated gerber file to complies with JLC rules.

## Usage

Make sure you have installed Python 3 on your system and configured properly.

Install KiJ-Patcher using pip.
`pip install kijpatcher`

```log
$ python3 -m kijpatcher
KiJ Patcher 1.0.0
Copyright (c) 2024-2025 Xina.
Copyright (c) 2023 ngHackerX86.
This is a free software released under GNU GPLv2. See LICENSE for more information.

usage: kijpatcher -i <input> -o <output>

Patch KiCad-generated gerber file to complies with JLC rules.

positional arguments:
  positional_input      Lazy mode, specify gerbers files directory only

options:
  -h, --help            show this help message and exit
  -i INPUT_FOLDER, --input-folder INPUT_FOLDER
                        PATH to gerber files directory
  -o OUTPUT_FILE, --output-file OUTPUT_FILE
                        PATH to output file, if FULL path is given. Otherwise, it specifies the output file name.
  -t {std,pro}, --version-string-type {std,pro}
                        Specify EasyEDA version type string in Gerber header

```

## Fabrication Output Settings

The following screenshots show the proper fabrication output settings when using KiJ-Patcher, which ensure KiJ-Patcher could recognize and patch the fabrication output files properly.

### Gerber Settings

![image](docs/fabrication_output_settings_gerber.png)

### Drill Settings

![image](docs/fabrication_output_settings_drill.png)

## Copyright and Credits

Copyright (c) 2024-2025 Xina.

Copyright (c) 2023 ngHackerX86.

## Disclaimers

JLC and EasyEDA are registered trademarks of Shenzhen JLC Technology Group Co., Ltd and its subsidiaries. We makes contextual use of the trademarks of Shenzhen JLC Technology Group Co., Ltd and its subsidiaries to indicate the function of the program.

We are not affiliated, associated, authorized, endorsed by, or in any way officially connected with Shenzhen JLC Technology Group Co., Ltd and its subsidiaries.
