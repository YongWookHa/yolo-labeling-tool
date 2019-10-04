'''
This codes ONLY create files below.
 - 'project_name.txt'   : contains all directories of which are '.jpg' or '.png' format  
 - 'project_name.name'  : stores all class name extracted from 'config.txt'

You still have to make 'project_name.data' file and '*.cfg' file.
Details could be found in https://github.com/ultralytics/yolov3/wiki/Train-Custom-Data
'''

import random
import shutil
from pathlib import Path
from tkinter.filedialog import askdirectory

if __name__ == "__main__":
    with open("config.txt", 'r', encoding='utf8') as f:
        lines = f.readlines()
        keys = []
        for line in lines:
            cfg = list(map(str.strip, line.split(':')))
            if 'project_name' in cfg[0]:
                project_name = cfg[1]
            if cfg[0][:3] == 'key' and cfg[1] is not '':
                keys.append(cfg[1])

    directory = Path(askdirectory())  # search all sub-directories

    with open(directory / (project_name+'.names'), 'w', encoding='utf8') as f:
        for key in keys:
            f.write(key+'\n')
        print('.names file save in ', directory / (project_name+'.names'))
    
    images = []
    for fileObject in directory.glob('**/*'):
        if fileObject.suffix in ('.jpg', '.png'):
            images.append(fileObject)
    
    all_files = list(directory.glob('**/*'))
    
    to_write = []
    for img in images:
        if str(img.with_suffix('.txt')) in all_files:
            print(str(img.with_suffix('.txt')), 'is not in all_files')
            continue
        to_write.append(img)

    if input('Split dataset into [train / test]? (y/n) : ') in ('yes', 'y'):
        train_ratio = float(input('Enter train data ratio (0 ~ 1) : '))
        random.shuffle(to_write)
        train_num = int(len(to_write) * train_ratio)
        train_data = to_write[:train_num]
        test_data = to_write[train_num:]

        with open(directory / (project_name+'_train.txt'), 'w', encoding='utf8') as f:
            for fileObject in train_data:
                f.write(str(fileObject)+'\n')
            print('Train data list saved in ', directory / (project_name+'_train.txt'))
        with open(directory / (project_name+'_test.txt'), 'w', encoding='utf8') as f:
            (directory / 'test_data').mkdir(exist_ok=True)
            for fileObject in test_data:
                f.write(str(fileObject)+'\n')
                shutil.copyfile(str(fileObject), str((directory / 'test_data' / fileObject.name)))
            print('Test data list saved in ', directory / (project_name+'_test.txt'))
            print('Test data copied at ', directory / 'test')

    else:
        with open(directory / (project_name+'_total.txt'), 'w', encoding='utf8') as f:
            for fileObject in to_write:
                f.write(str(fileObject)+'\n')
            print('Total data saved in ', directory / (project_name+'_total.txt'))

    input("\nPress any button to exit")
 