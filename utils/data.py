



import argparse
import os
import shutil

'''
##############################################################Classify image for file name and split it to directory with image name##############################################################
'''


IMG_FORMAT={'.png','.jpg','.jpeg'}


def classify_img_to_dir(load_path,save_path):
    '''
    Classify image for file name and split it to directory with file name
    :return:
    '''


    try:
        for file_name in os.listdir(load_path):
            parser=os.path.splitext(file_name)
            name=parser[0]
            format=parser[1]

            if format.lower() in IMG_FORMAT:
                dir_path=os.path.join(save_path,name)
                if not(os.path.isdir(dir_path)):
                    os.makedirs(dir_path)
                    print('Success to create directory : {}'.format(dir_path))

                shutil.copy(os.path.join(load_path,file_name),os.path.join(dir_path,file_name))# Move load_path to save_path
                print('Success to move file : {}\n'.format(os.path.join(dir_path,file_name)))


    except Exception as e:
        print('Error : {}'.format(e))


