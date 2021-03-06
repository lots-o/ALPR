



import argparse
import os
import shutil
import Augmentor
from abc import * # Abstract base clss
import cv2
import random
import plate_dataset.info as plate_info



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


'''
##############################################################Synthetic korean auto-license-plate generator ##############################################################
'''




class LicensePlateFactory():
    '''
    License Plate Creator
    '''

    @staticmethod
    def create_license_plate(type,plate_path,num_path,char_path,region_path=None,save_path=None,debug=False):

        TYPE={'TYPE1','TYPE2','TYPE3','TYPE4','TYPE5','TYPE6'}
        assert type in TYPE, f'Available type : {TYPE}' 

        config=(plate_path,num_path,char_path,region_path,save_path,debug)
        if type == 'TYPE1':
            return LicensePlateType1(*config)
        elif type == 'TYPE2':
            return LicensePlateType2(*config)
        elif type == 'TYPE3':
            return LicensePlateType3(*config)
        elif type == 'TYPE4':
            return LicensePlateType4(*config)
        elif type == 'TYPE5':
            return LicensePlateType5(*config)
        elif type == 'TYPE6':
            return LicensePlateType6(*config)


class LicensePlateTemplate(metaclass=ABCMeta):
    '''
    License Plate Template
    '''
    def __init__(self,plate_path,num_path,char_path,region_path=None,save_path=None,debug=False):
        self.plate_path=plate_path
        self.num_path=num_path
        self.char_path=char_path
        self.region_path=region_path
        self.save_path=save_path
        self.debug=debug

    def load_images(self,path):
        images=[]
        file_names=[]
        try:
            for file_name in os.listdir(path):
                parser=os.path.splitext(file_name)
                name=parser[0]
                format=parser[1]
                if format.lower() in IMG_FORMAT:
                    img_path=os.path.join(path,file_name)
                    images.append(cv2.imread(img_path))
                    file_names.append(name)
        except Exception as e:
            raise e


        return images,file_names 

    @abstractmethod
    def draw(self,n_samples):
        pass

class LicensePlateType1(LicensePlateTemplate):
    '''
    Non business small white plate 335-155 , single line
    '''

    def draw(self,n_samples):
        

        plate,_=self.load_images(self.plate_path)
        assert len(plate) == 1 , ('The source directory of plate must contain only one image')
        nums,_=self.load_images(self.num_path)
        chars,chars_name=self.load_images(self.char_path)

        #Resizing
        plate=cv2.resize(plate[0],(plate_info.NON_BUSINESS_S_WHITE_PLATE_WIDTH,plate_info.NON_BUSINESS_S_WHITE_PLATE_HEIGHT))

        nums=[cv2.resize(num,(plate_info.NON_BUSINESS_S_WHITE_PLATE_NUM_WIDTH,plate_info.NON_BUSINESS_S_WHITE_PLATE_NUM_HEIGHT))\
              for num in nums]

        chars = [cv2.resize(char,(plate_info.NON_BUSINESS_S_WHITE_PLATE_CHAR_WIDTH,plate_info.NON_BUSINESS_S_WHITE_PLATE_CHAR_HEIGHT))\
              for char in chars]

        #Draw
        for _ in range(n_samples):
            file_name=''
            y=plate_info.NON_BUSINESS_S_WHITE_PLATE_TOP_INTERVAL
            x=plate_info.NON_BUSINESS_S_WHITE_PLATE_LEFT_INTERVAL
            for i in range(plate_info.NON_BUSINESS_S_WHITE_PLATE_LENGTH):
                if i==2: #char
                    rand_char=random.randint(0,len(chars)-1)
                    plate[y:y + plate_info.NON_BUSINESS_S_WHITE_PLATE_CHAR_HEIGHT, \
                    x:x + plate_info.NON_BUSINESS_S_WHITE_PLATE_CHAR_WIDTH] = chars[rand_char]
                    x += plate_info.NON_BUSINESS_S_WHITE_PLATE_CHAR_WIDTH
                    file_name+=chars_name[rand_char]
                else:# num
                    rand_num=random.randint(0,len(nums)-1)
                    plate[y:y + plate_info.NON_BUSINESS_S_WHITE_PLATE_NUM_HEIGHT, \
                    x:x + plate_info.NON_BUSINESS_S_WHITE_PLATE_NUM_WIDTH] = nums[rand_num]
                    x+=plate_info.NON_BUSINESS_S_WHITE_PLATE_NUM_WIDTH
                    file_name+=str(rand_num)

            if self.debug:
                cv2.imshow(file_name,plate)
                cv2.waitKey()
                cv2.destroyAllWindows()
            
            if self.save_path:
                cv2.imwrite(f'{file_name}.jpg',plate)
                print(f'Saved "{file_name}" --> "{self.save_path}"')
            


class LicensePlateType2(LicensePlateTemplate):
    '''
    Non business large 2-digit white plate 520-110 , single line
    '''


    def draw(self,n_samples):

        plate,_ = self.load_images(self.plate_path)
        assert len(plate) == 1, ('The source directory of plate must contain only one image')
        nums,_= self.load_images(self.num_path)
        chars,chars_name = self.load_images(self.char_path)

        # Resizing
        plate = cv2.resize(plate[0],
                           (plate_info.NON_BUSINESS_L_2_DIGIT_WHITE_PLATE_WIDTH, plate_info.NON_BUSINESS_L_2_DIGIT_WHITE_PLATE_HEIGHT))

        nums = [cv2.resize(num, (
        plate_info.NON_BUSINESS_L_2_DIGIT_WHITE_PLATE_NUM_WIDTH, plate_info.NON_BUSINESS_L_2_DIGIT_WHITE_PLATE_NUM_HEIGHT)) \
                for num in nums]

        chars = [cv2.resize(char, (
        plate_info.NON_BUSINESS_L_2_DIGIT_WHITE_PLATE_CHAR_WIDTH, plate_info.NON_BUSINESS_L_2_DIGIT_WHITE_PLATE_CHAR_HEIGHT)) \
                 for char in chars]

        # Draw

        for _ in range(n_samples):
            file_name=''
            y = plate_info.NON_BUSINESS_L_2_DIGIT_WHITE_PLATE_TOP_INTERVAL
            x = plate_info.NON_BUSINESS_L_2_DIGIT_WHITE_PLATE_LEFT_INTERVAL
            for i in range(plate_info.NON_BUSINESS_L_2_DIGIT_WHITE_PLATE_LENGTH):

                if i == 2:  # char
                    rand_char = random.randint(0, len(chars) - 1)
                    plate[y:y + plate_info.NON_BUSINESS_L_2_DIGIT_WHITE_PLATE_CHAR_HEIGHT, \
                    x:x + plate_info.NON_BUSINESS_L_2_DIGIT_WHITE_PLATE_CHAR_WIDTH] = chars[rand_char]
                    x += plate_info.NON_BUSINESS_L_2_DIGIT_WHITE_PLATE_CHAR_WIDTH
                    file_name+=chars_name[rand_char]
                    
                else: # num
                    rand_num = random.randint(0, len(nums) - 1)
                    plate[y:y + plate_info.NON_BUSINESS_L_2_DIGIT_WHITE_PLATE_NUM_HEIGHT, \
                    x:x + plate_info.NON_BUSINESS_L_2_DIGIT_WHITE_PLATE_NUM_WIDTH] = nums[rand_num]
                    x += plate_info.NON_BUSINESS_L_2_DIGIT_WHITE_PLATE_NUM_WIDTH
                    file_name+=str(rand_num)

            if self.debug:
                cv2.imshow(file_name,plate)
                cv2.waitKey()
                cv2.destroyAllWindows()
            
            if self.save_path:
                cv2.imwrite(f'{file_name}.jpg',plate)
                print(f'Saved "{file_name}" --> "{self.save_path}"')
                


class LicensePlateType3(LicensePlateTemplate):
    '''
    Non business large 3-digit old white plate 520-110 , single line
    '''

    def draw(self,n_samples):
        pass

class LicensePlateType4(LicensePlateTemplate):
    '''
    Non business 3-digit new white plate 520-110 , single line -> Type4
    '''



    def draw(self,n_samples):
        pass

class LicensePlateType5(LicensePlateTemplate):
    '''
    Business small yellow plate 335-170 , multi lines -> Type5
    '''




    def draw(self,n_samples):
        pass
class LicensePlateType6(LicensePlateTemplate):
    '''
    Business large yellow plate 520-110 , single lines -> Type6
    '''

    def draw(self,n_samples):
        pass



if __name__== '__main__':
    plate_type_1=LicensePlateFactory().create_license_plate(
        type='TYPE1',
        plate_path='utils/plate_dataset/type1/plate',
        num_path='utils/plate_dataset/type1/num',
        char_path='utils/plate_dataset/type1/char',
        save_path='./'

    )
    plate_type_2=LicensePlateFactory().create_license_plate(
        type='TYPE2',
        plate_path='utils/plate_dataset/type2/plate',
        num_path='utils/plate_dataset/type2/num',
        char_path='utils/plate_dataset/type2/char',
        save_path='./'

    )
    # plate_type_1.draw(10)
    plate_type_2.draw(10)







































