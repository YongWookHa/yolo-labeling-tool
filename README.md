# yolo-labeling-tool

## 1. Overview

Python based GUI for marking bounded boxes of objects in images for training Yolo v3 and v2 [https://github.com/AlexeyAB/darknet](https://github.com/AlexeyAB/darknet). You can generate your own **YOLO format** custom data with `yolo-labeling-tool`.

You should put the files listed below together. 

> #### - main.py
>
> contains the main codes.
>
> #### - config.json
>
> ```bash
> project_name : "str"
> key_1 : label_name_1 
>  key_2 : label_name_2
> ...
> key_9 : label_name_9
> ```
> The class number(label number) which would be stored in the result file started from 0.
> 
> These configs must follow the json format.
> 
> #### - images
> * start.png : show when the job started
> * end.png : show when the job finished
> 
> Of course, you can use your own images.
>
> #### - create_file_list.py
>  
> After marking bounding boxes and labelling, you need to make `.data`, `.names`, list of `train data` and `test data` files. This python codes will help you to write those files with simple action. 

 
## 2. Get Ready

First of all, install the dependecies.
```bash
pip install -r requirements.txt
```

Before start the program, edit `config.json` file as your needs. 

Now, you can run the program by simply executing the code with python.

```bash
python main.py
```

## 3. Usage

You need to 

Now, you are ready to start generating you own train data.

![capture (2)](https://user-images.githubusercontent.com/12293076/66543692-09d07900-eb71-11e9-8122-9168319e4f67.PNG)

You will see the window above. Press `Input Path` button and select a directory where your training images are. If you check `Crop Mode`, your bounding boxes will be saved separately by cropping. You can specify where crop results to be saved by pressing `Save Path` button. And then, press `Next` button to start the main process.

Now, you can draw bounding boxes by draging on the image. After drawing a box, you should tag the box by pressing <kbd>1-9</kbd>. The `num:label name` setting should be specified in `config.json` in advance. You can change the last box's tag by pressing tagging button again. If you find earlier mistakes, then remove the wrongly drawn box by clicking it with <kbd>Right</kbd> mouse button.

Each time you click `Next` button or press <kbd>E</kbd>, your work will be saved image by image in a `.txt` file which has same filename of the image.

For now, if you want to edit boxes of previous image, you need to delete the txt file of that image.

For writing nessesary files for training Yolo, run `create_file_list.py`. Select a directory where **all** data are. Answer whether you want to split the data into train and test or not. If yes, enter the train data ratio. Then those four files below will be automatically generated. 

* `.data` : comprehensive information
* `.names` : class information
* `train data` : list of train data directory
* `test data` : list of test(validate) data directory

And it will copy the test data images in `test_data` directory. The only thing left is making `.cfg` file which represent the inner structure of your network. `yolo-labeling-tool` cannot help you make `.cfg`. Find out the details of building custom data in [ultralytics/yolov3](https://github.com/ultralytics/yolov3/wiki/Train-Custom-Data).

#### Mouse control

Button | Description | 
--- | --- |
<kbd>Left</kbd> | Draw box
<kbd>Right</kbd> | Remove box

#### Keyboard Shortcuts

Shortcut | Description | 
--- | --- |
<kbd>1-9</kbd> | Tag the last box |
<kbd>ESC</kbd> | Cancel The Last Box |
<kbd>Q</kbd> | Cancel All Boxes |
<kbd>E</kbd> | Next button |


## 4. ETC

If you want to build `.exe` file, use [pyinstaller](https://github.com/pyinstaller/pyinstaller).
```bash
pip install pyinstaller
pyinstaller --onefile --noconsole main.py
```
_You need to carry `config.json`, `start.png`, `end.png` with your `.exe` as well._

## 5. author
| | |
| --- | --- |
| github | [https://github.com/YongWookHa/](https://github.com/YongWookHa/) |
| e-mail | ywha12@gmail.com |

enjoy the code.