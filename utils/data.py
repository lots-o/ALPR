



import argparse
import os
import shutil
import Augmentor
from abc import * # Abstract base clss

IMG_FORMAT={'.png','.jpg','.jpeg'}

'''
##############################################################Classify image for file name and split it to directory with image name##############################################################
'''

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
        raise e



'''
##############################################################Augmentation##############################################################
'''

class AugmentationHelper(metaclass=ABCMeta):
    '''
    Note!!
    Augmentor will only work if the source directories contain basically nothing but images.
    It was not designed to filter out images from a directory which might contains other files and folders
    '''
    def __init__(self,n_samples):
        self.n_samples=n_samples
        self.excluded_dir='output'

    @abstractmethod
    def augmentation(self,path):
        pass

    def check_file_structure(self,path):
        '''
        :param path:
        :return: dirs,images
        '''
        dirs=[]
        images=[]
        for file_name in os.listdir(path):
            file=os.path.join(path,file_name)
            parser=os.path.splitext(file_name)
            format=parser[1]
            if os.path.isdir(file) and file_name !=self.excluded_dir:
                dirs.append(file)
            elif format.lower() in IMG_FORMAT:
                images.append(file_name)

        return dirs,images


    def run(self,path):
        '''
        First, Check to source directory whether it can augment (=The source directory must contain basically nothing but images)
        Second, If can, run to augmentation.
        Third, If not, recursively, search to dirs until find valid sourch directory
        :return:
        '''

        dirs,images=self.check_file_structure(path) # First
        if dirs == [] and len(images)>=1: # Second
            # augmentation
            self.augmentation(path)

        else: # Third, dirs !=[] or len(images) == 0
            if len(images)>=1: # dirs !=[]
                print('Augmentation will only work if the source directories contain basically nothing but images')
                print('Failed to augment, path : {}'.format(path))
            else:
                for dir in dirs:
                    self.run(dir)

class CustomAugmentation(AugmentationHelper):

    types={'TYPE_1','TYPE_2','TYPE_3','TYPE_4','TYPE_5','TYPE_6','TYPE_7'}

    def __init__(self,n_samples,type='TYPE_1'):
        super(CustomAugmentation, self).__init__(n_samples)
        if type not in CustomAugmentation.types:
            raise Exception('Available type : TYPE_1 ~ TYPE_7')
        self.type=type


    def augmentation(self,path):
        p=Augmentor.Pipeline(path)
        # p.resize(probability=1.0,width=56,height=56)
        p.greyscale(1.0)


        if self.type =='TYPE_1':
            p.skew_left_right(probability=1.0,magnitude=0.5) # maximum skew = magnitude 0.1 ~ 1.0
        elif self.type == 'TYPE_2':
            p.skew_top_bottom(1.0,magnitude=0.1)

        elif self.type == 'TYPE_3':
            p.rotate(1.0,max_left_rotation=10,max_right_rotation=10)

        elif self.type == 'TYPE_4': # TYPE_1+TYPE_3
            p.rotate(1.0,max_left_rotation=10,max_right_rotation=10)
            p.skew_left_right(probability=1.0,magnitude=0.3) # maximum skew = magnitude 0.1 ~ 1.0

        elif self.type == 'TYPE_5' : # Type2 + Type3
            p.rotate(1.0, max_left_rotation=10, max_right_rotation=10)
            p.skew_top_bottom(1.0,magnitude=0.1)

        elif self.type == 'TYPE_6' :
            p.shear(1.0,max_shear_left=10,max_shear_right=10)

        elif self.type == 'TYPE_7':
            p.rotate(1.0,max_left_rotation=10,max_right_rotation=10)
            p.shear(1.0,max_shear_left=5,max_shear_right=5)

        p.sample(self.n_samples)


# classify_img_to_dir('dataset','augmented_data')
# for type in CustomAugmentation.types:
#     augmentor = CustomAugmentation(n_samples=200, type=type)
#     augmentor.run('augmented_data')








































