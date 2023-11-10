import pandas as pd
from DBManager import DB_Manager
import os 
import re

if __name__ == '__main__':
    pd.options.display.max_columns = 400
    pd.options.display.max_rows = 1200
    pd.options.display.max_colwidth = 50
    table_name = 'M15_DAILY_WORKS'
    db_manager = DB_Manager()
    ## 테이블을 초기화한다. 
    db_manager.delete_rows(table_name)
    # dir = 'D:/0. 보고/일일보고/2022/'
    dir = 'C:/Users/Dinno/Downloads/일일보고/2023/'
    list = os.listdir(dir)
    file_pathes = []
    for i in range(1,12):
        try:
            dir_month = dir+str(i)+'월'
            list = os.listdir(dir_month)
            list.sort()
            for li in list:
                p = re.compile('[1-9]')
                res = p.findall(li)
                if len(res) > 0:
                    #바로 파일일때 파일 리스트 만들기
                    if li.endswith('xlsx') == True:
                        file_pathes.append(dir_month+"/"+li)
                    #한 단계 폴더가 더 있을때 리스트 만들기(폴더 이름과 파일 이름 비교)
                    else:
                        excel = os.listdir(dir_month+'/'+li)
                        for ex in excel:
                        ## 폴더안에 xlsx파일이 여러개 있으므로 날짜와 같은지 폴더이름과 파일이름을 비교한다. 20220105 == 일일보고_20220105.xlsx => [5:-5]
                            if ex.endswith('xlsx') and ex[5:-5]==li:
                                ## 바로 파일인 애들은 li(파일이름)을 붙이고
                                ## 일일마다 폴더가 있다면 날짜이름 폴더 + 파일이름
                                file_pathes.append(dir_month+"/"+li+"/"+ex)
        except Exception as e:
            print(e)
    # import pandas as pd

    # df = pd.read_excel(file_pathes[0],sheet_name='일일업무')
    # pd.set_option('display.max_rows', 500)
    # pd.set_option('display.max_columns', 500)
    # pd.set_option('display.width', 1000)
    # print(df.drop(['Unnamed: 3'],axis=1)
    db_manager.file_path_to_db(table_name, file_pathes)
    # df = db_manager.read_table()
    # df_1 = df[df['Name']=='방태훈']
    # print(df_1)
