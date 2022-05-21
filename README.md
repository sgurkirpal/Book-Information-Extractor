# cs305_2022

Submitter name: Gurkirpal Singh

Roll No.: 2019csb1087

Course: CS305

=================================

## 1. What does this program do?

- The program develop an application which extracts the metadata from a collection of book cover pages. 
- The cover pages of an book are scanned images (taken as a single image file) of the first few pages of the book.
- The following information needs to be extracted:
    - Title of the book
    - Names of the authors
    - Publishers
    - ISBN numbers
- Input can be the path of an image or path of a folder containing a number of images depending on the flag.


## 2. A description of how this program works (i.e. its logic)

- main.py is the main code file for the assignment. 

- It takes a flag and a path as argument.

- If flag is 0, path of a single image is passed, else if flag is 1, path of a folder containing many images is passed. The image is then passed into the OCR and after that title, authors, publishers and ISBN number of the image are extracted. 

- For the OCR, pytesseract library is used. First, the contrast of the image passed is increased by a factor of 1.9 and then it is converted to the grayscale.

- For extracting title:
    - image_to_data function is used, which also outputs the height,width and confidence value for the text. 
    - Some preprocessing is done to prevent noise. Then all words with confidence value less than 70 are rejected. 
    - After that, the word with maximum height is selected as the title of the book.

- For extracting author names:
    - image_to_string function is used, which outputs the string of all the words detected. 
    - The string is then passed into the nlp model which is built in the spacy library to detect the person names. 
    - All the names extracted are labelled as the authors of the book.

- For extracting ISBN number: 
    - image_to_string function is used, which outputs the string of all the words detected. 
    - The string is then searched for the word ISBN and the numbers following the word ISBN are extracted and returned as the ISBN number of the book. 
    - If the ISBN is present without the word ISBN, then any number of lenghth 9-15 present in the string is returned.

- For extracting publisher details: 
- image_to_string function is used, which outputs the string of all the words detected. 
- The string is then passed into the nlp model which is built in the spacy library to detect the organisation names. 
- All the organisations extracted are labelled as the publishers of the book.

## 3. How to compile and run this program

- Running the program file(main.py): `python3 main.py --flag 0 --path /home/gurkirpal/sde/assignment_3/test_folder/book.png` or `python3 main.py --flag 1 --path /home/gurkirpal/sde/assignment_3/test_folder`.
- Tests are implemented using pytest. Running tests: `pytest test.py`
- To get the coverage: run

```
    coverage run -m --omit=/usr/* pytest test.py
    coverage report
```

## 4. Provide a snapshot of a sample run

- Snapshots are attached in a folder named ScreenShots.

## 5. Github Link

https://github.com/sgurkirpal/cs305_2022

## 6. Results

- I am getting a coverage of 91%. Screenshot is attached in a folder named Screenshots.
