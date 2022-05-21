from main import main_main
import os

def test_1():
    result=list(main_main(0,"/home/gurkirpal/sde/assignment_3/test_folder/book.png"))
    print(result)
    assert result[0]=="Agile Methodology"
    assert result[2]=="978-0-618-26030-0"

def test_2():
    # print(os.system("python3 main.py --flag 1 --path /home/gurkirpal/sde/assignment_3/test_folder"))
    result=list(main_main(1,"/home/gurkirpal/sde/assignment_3/test_folder"))
