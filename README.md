# yolo-labeling-tool

## Overview

Python based GUI for marking bounded boxes of objects in images for training Yolo v3 and v2 [https://github.com/AlexeyAB/darknet](https://github.com/AlexeyAB/darknet). You can generate the **YOLO format** custom data with this program.

You should put the files listed below together. 

#### main.py

> `main.py` contains all the codes.

#### config.txt

> ```
> max_height : int
> key_1 : label_name_1 
> key_2 : label_name_2
> ...
> key_9 : label_name_9
> ```
> The class number(label number) which would be stored in the result file started from 0.
>
> These configs must follow the original format.

#### images
> * start.png : show when the job started
> * end.png : show when the job finished
>
>Of course, you can use your own images.

## Usage

First of all, install the dependecies.
```bash
pip install -r requirements.txt
```

Then, you can simply execute the code with python.
```bash
python main.py
```

**_Backup your image before run the program since it will resize your original image._**

#### Mouse control

Button | Description | 
--- | --- |
<kbd>Left</kbd> | Draw box
<kbd>Right</kbd> | Remove box

#### Keyboard Shortcuts

Shortcut | Description | 
--- | --- |
<kbd>0-9</kbd> | Object id |
<kbd>ESC</kbd> | Cancel the last box |
<kbd>space</kbd> | Next image |



## ETC

If you want to build `exe` file, use [pyinstaller](https://github.com/pyinstaller/pyinstaller).
```bash
pip install pyinstaller
pyinstaller --onefile --noconsole main.py
```

## author
| | |
| --- | --- |
| github | [https://github.com/YongWookHa/](https://github.com/YongWookHa/) |
| e-mail | ywha12@gmail.com |

enjoy the code.