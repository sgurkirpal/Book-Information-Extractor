'''
    This is the main code file for the assignment. It takes a flag and a path as argument
    and if flag is 0, path of a single image is passed, else if flag is 1, path of a folder 
    containing many images is passed. The image is then passed into the OCR and after that 
    title, authors, publishers and ISBN number of the image are extracted. 
    
    For the OCR, pytesseract library is used. First, the contrast of the image passed is 
    increased by a factor of 1.9 and then it is converted to the grayscale.
    
    For extracting title, image_to_data function is used, which also outputs the height,
    width and confidence value for the text. Some preprocessing is done to prevent noise.
    Then all words with confidence value less than 70 are rejected. After that, the word
    with maximum height is selected as the title of the book.

    For extracting author names, image_to_string function is used, which outputs the string
    of all the words detected. The string is then passed into the nlp model which is built in 
    the spacy library to detect the person names. All the names extracted are labelled as the 
    authors of the book.

    For extracting ISBN number, image_to_string function is used, which outputs the string
    of all the words detected. The string is then searched for the word ISBN and the numbers
    following the word ISBN are extracted and returned as the ISBN number of the book. If the
    ISBN is present without the word ISBN, then any number of lenghth 9-15 is returned.

    For extracting publisher details, image_to_string function is used, which outputs the string
    of all the words detected. The string is then passed into the nlp model which is built in 
    the spacy library to detect the organisation names. All the organisations extracted are labelled 
    as the publishers of the book.
'''

from multiprocessing.dummy import Process
import re
from PIL import Image, ImageEnhance, ImageFilter,ImageOps
from numpy import size
import pytesseract
import argparse
from abc import abstractmethod,ABC
import spacy
import os
# import openpyxl
import pandas as pd
import xlsxwriter


'''
    This is an abstract class for processing the images. Its subclasses would be
    images of different extensions like png/jpg or jpeg or other. Currently, we 
    have subclass for jpg/png format but it can be extended for other image types.
'''
class ProcessImage(ABC):
    @abstractmethod

    # method to extract the title from the image.
    def getTitle():
        pass

    # method to extract the authors from the image.
    def getAuthors():
        pass

    # method to extract the ISBN from the image.
    def getISBN():
        pass

    # method to extract the publisher from the image.
    def getPublisher():
        pass


# This class is responsible for the preprocessig related to OCR of the image.
# Python inbuilt OCR that is the pytesserect is not that effective if used 
# without any preprocessing, So image needs to be editted.
class EnhanceImage:
    im=None

    # This function increases the contrast of the image by a factor of 1.9 
    # and then convert it into grayscale before extracting data.
    def enhance(self,image):
        enhancer = ImageEnhance.Contrast(image)
        self.im = enhancer.enhance(1.9)
        self.im=ImageOps.grayscale(self.im)
        # self.im.show()
        # self.im.save('temp.jpg')


    # This function is used for extracting the title from the image. image_to_data function
    # is used to get all the information.
    def toData(self,image):
        # im.show()
        self.enhance(image)
        text = pytesseract.image_to_data(self.im,output_type="dict")
        return text

    # This function is used for extracting the authors,publisher and ISBN from the image. 
    # image_to_string function
    # is used to get only the words from the image.
    def toString(self,image):
        # im=ImageOps.grayscale(image)
        # im.save('temp2.jpg')
        # im.show()
        self.enhance(image)
        text = pytesseract.image_to_string(self.im,output_type="dict")
        my_text=text["text"]
        my_text=my_text.replace("\n","  ")
        # print(text)
        # print(my_text)
        return my_text
        

# this is a subclass of the abstract class ProcessImage.
# This is for the image times jpg and png.
class ProcessJPG_and_PNG(ProcessImage):
    data=[]
    im=None
    text=None

    # The method returns a dictionary for the words of different sizes/heights.
    # Words of same height are merged to form a single sentence.
    def getSizeDict(self):
        size_dict={}
        for i in range(len(self.text["height"])):
            if(self.text["text"][i]==" " or self.text["text"][i]=="|" or self.text["text"][i]==""):
                continue
            ww=0
            for j in self.text["text"][i]:
                if j!=" ":
                    ww=1
                    break
            if(ww==0):
                continue
            if(self.text["conf"][i]<70):
                continue
            if self.text["height"][i] in size_dict:
                sam=self.text["height"][i]
                size_dict[self.text["height"][i]]+=" "
                size_dict[sam]+=self.text["text"][i]
            else:
                size_dict[self.text["height"][i]]=self.text["text"][i]
        # for i in size_dict:
        #     print(i,size_dict[i])
        return size_dict
        

    # method to extract the title from the image.
    # For extracting title, image_to_data function is used, which also outputs the height,
    # width and confidence value for the text. Some preprocessing is done to prevent noise.
    # Then all words with confidence value less than 70 are rejected. After that, the word
    # with maximum height is selected as the title of the book.
    def getTitle(self,image):
        enhancer=EnhanceImage()
        self.text=enhancer.toData(image)
        size_dict=self.getSizeDict()
        maxo=0
        max_ind=-1
        sma=""
        for i in size_dict:
            if(i>maxo):
                if(i-maxo<=5):
                    sam+=" "
                    sam+=size_dict[i]
                    maxo=i
                    max_ind=i
                else:
                    sam=size_dict[i]
                    maxo=i
                    max_ind=i
            else:
                if(maxo-i<=5):
                    sam+=" "
                    sam+=size_dict[i]
        if max_ind==-1:
            return ""
        return sam

    # method to extract the authors from the image.
    # For extracting author names, image_to_string function is used, which outputs the string
    # of all the words detected. The string is then passed into the nlp model which is built in 
    # the spacy library to detect the person names. All the names extracted are labelled as the 
    # authors of the book.
    def getAuthors(self,image):
        enhancer=EnhanceImage()
        text=enhancer.toString(image)
        doc=nlp(text)
        # print(doc)
        persons= [ent.text for ent in doc.ents if ent.label_ == 'PERSON']
        # print(persons)
        return str(persons)

    # method to extract the ISBN from the image.
    # For extracting ISBN number, image_to_string function is used, which outputs the string
    # of all the words detected. The string is then searched for the word ISBN and the numbers
    # following the word ISBN are extracted and returned as the ISBN number of the book. If the
    # ISBN is present without the word ISBN, then any number of lenghth 9-15 is returned.
    def getISBN(self,image):
        enhancer=EnhanceImage()
        text=enhancer.toString(image)
        ind=text.find("ISBN")
        if(ind==-1):
            sample=text.replace("-","")
            all_numbers=re.findall('[0-9]+',sample)
            for i in all_numbers:
                if len(i)>=9 and len(i)<=15:
                    return i
            return ""
        sam=""
        for i in range(ind+5,len(text)):
            if(text[i]==" "):
                break
            else:
                sam+=text[i]
        # print(sam)
        return sam


    # method to extract the publishers from the image.
    # For extracting publisher details, image_to_string function is used, which outputs the string
    # of all the words detected. The string is then passed into the nlp model which is built in 
    # the spacy library to detect the organisation names. All the organisations extracted are labelled 
    # as the publishers of the book.
    def getPublisher(self,image):
        enhancer=EnhanceImage()
        text=enhancer.toString(image)
        doc=nlp2(text)
        # print(doc)
        orgs= [ent.text for ent in doc.ents if ent.label_ == 'ORG']
        # print(orgs)
        return str(orgs)


# The function takes path of the image as parameter and returns the required information.
def main(image_path):
    
    im = Image.open(image_path)
    driver=ProcessJPG_and_PNG()
    path="ouput.xlsx"
    # wb= openpyxl.Workbook()
    # ws=wb.active
    # with pd.ExcelWriter(path,engine="openpyxl") as writer:
    #     # df=pd.read_excel(path.read(), engine='openpyxl')

    #     writer.book = wb
    #     writer.sheets = dict((ws.title, ws) for ws in wb.worksheets)
    #     print(writer.book)
    #     df=pd.DataFrame([driver.getTitle(im),driver.getAuthors(im),driver.getISBN(im),driver.getPublisher(im)],columns=["Title","Authors","ISBN","Publisher"])
    #     # df.to_excel(path,sheet_name="Sheet1")
    #     print(df)
    return [driver.getTitle(im),driver.getAuthors(im),driver.getISBN(im),driver.getPublisher(im)]

def main_main(flag,path):
    global nlp,nlp2
    nlp=spacy.load("en_core_web_md")
    nlp2=spacy.load("en_core_web_sm")
    workbook = xlsxwriter.Workbook('Output.xlsx')
    worksheet = workbook.add_worksheet()
    worksheet.write(0,0,'Image')  
    worksheet.write(0,1,'Title') 
    worksheet.write(0,2,'Authors') 
    worksheet.write(0,3,'ISBN Number')
    worksheet.write(0,4,'Publishers')
    if(flag==0):
        sam=main(path)
        print(sam)
        worksheet.write(1,0,1)
        worksheet.write(1,1,sam[0])
        worksheet.write(1,2,sam[1])
        worksheet.write(1,3,sam[2])
        worksheet.write(1,4,sam[3])
        workbook.close()
        return sam
    elif(flag==1):
        dirs=os.listdir(path)
        result=[]
        cnt=1
        for i in dirs:
            sam=main(os.path.join(path,i))
            worksheet.write(cnt,0,cnt)
            worksheet.write(cnt,1,sam[0])
            worksheet.write(cnt,2,sam[1])
            worksheet.write(cnt,3,sam[2])
            worksheet.write(cnt,4,sam[3])
            cnt+=1
            result.append(sam)
        workbook.close()
        return result
    else:
        print("Incorrect flag")
        workbook.close()
        return []
        

if __name__=="__main__":
    # Flag and path arguments are required
    parser = argparse.ArgumentParser()
    parser.add_argument('--flag', type=int, required=True)
    parser.add_argument('--path', type=str, required=True)
    args = parser.parse_args()
    main_main(args.flag,args.path)








# im = im.filter(ImageFilter.MedianFilter())
# enhancer = ImageEnhance.Contrast(im)
# im = enhancer.enhance(1)
# enhancer = ImageEnhance.Sharpness(im)
# im = enhancer.enhance(5)
# enhancer = ImageEnhance.Color(im)
# im = enhancer.enhance(5)
# enhancer = ImageEnhance.Brightness(im)
# im = enhancer.enhance(1)
# im = im.convert('1')

# wid,ht=im.size
# for x in range(wid):
#     for y in range(ht):
#         coordinate=x,y
#         sam=im.getpixel(coordinate)
#         if(sam==255):
#             # print("hi")
#             im.putpixel(coordinate,0)
