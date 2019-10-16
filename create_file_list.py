'''
This codes ONLY create files below.
 - 'project_name.txt'   : contains all directories of which are '.jpg' or '.png' format  
 - 'project_name.name'  : stores all class name extracted from 'config.txt'

You still have to make '*.cfg' file.
Details could be found in https://github.com/ultralytics/yolov3/wiki/Train-Custom-Data
'''
import json
import random
import shutil
from pathlib import Path
from tkinter.filedialog import askdirectory

def getConfigFromJson(self, json_file):
    # parse the configurations from the config json file provided
    with open(json_file, 'r') as config_file:
        try:
            config_dict = json.load(config_file)
            # EasyDict allows to access dict values as attributes (works recursively).
            return config_dict
        except ValueError:
            print("INVALID JSON file format.. Please provide a good json file")
            exit(-1)

if __name__ == "__main__":
    with open("config.json", 'r') as f:
        try:
            config_dict = json.load(f)
            # EasyDict allows to access dict values as attributes (works recursively).
        except ValueError:
            print("INVALID JSON file format.. Please provide a good json file")
            exit(-1)
        keys = []
        for k, v in config_dict.items():
            if k == 'project_name':
                project_name = v
            elif 'key' in k and v is not '':
                keys.append(v)
        try:
            print('project name : ', project_name)
        except NameError:
            project_name = 'my_project'

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
    
    data_split = input('Split dataset into [train / test]? (y/n) : ') in ('yes', 'y')
    if data_split:
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

    with open(directory / (project_name+'.data'), 'w', encoding='utf8') as f:
        f.write('classes={}\n'.format(len(keys)))
        if data_split:
            f.write('train={}\n'.format(directory / (project_name+'_train.txt')))
            f.write('valid={}\n'.format(directory / (project_name+'_test.txt')))
        else:
            f.write('train={}\n'.format(directory / (project_name+'_total.txt')))
            f.write('valid={}\n'.format(directory / (project_name+'_total.txt')))
        f.write('names={}\n'.format(directory / (project_name+'.names')))
        f.write('backup=backup/\n')
        f.write('eval=eval\n')

    input("\nPress any button to exit")
 
