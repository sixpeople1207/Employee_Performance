# import pandas as pd
# from DBManager import DB_Manager
# import os 
# import re

# if __name__ == '__main__':
#     pd.options.display.max_columns = 400
#     pd.options.display.max_rows = 1200
#     pd.options.display.max_colwidth = 50
#     table_name = 'M15_DAILY_WORKS'
#     db_manager = DB_Manager()
#     ## 테이블을 초기화한다. 
#     db_manager.delete_rows(table_name)
#     # dir = 'D:/0. 보고/일일보고/2022/'
#     dir = 'C:/Users/Dinno/Downloads/일일보고/2023/'
#     list = os.listdir(dir)
#     file_pathes = []
#     try:
#         for i in range(1,12): ## Range는 (1,12) 일때 11까지 Roop
#                 dir_month = dir+str(i)+'월'
#                 list = os.listdir(dir_month)
#                 list.sort()
#                 for li in list:
#                     p = re.compile('[1-9]')
#                     res = p.findall(li)
#                     if len(res) > 0:
#                         #바로 파일일때 파일 리스트 만들기
#                         if li.endswith('xlsx') == True:
#                             file_pathes.append(dir_month+"/"+li)
#                         #한 단계 폴더가 더 있을때 리스트 만들기(폴더 이름과 파일 이름 비교)
#                         else:
#                             excel = os.listdir(dir_month+'/'+li)
#                             for ex in excel:
#                             ## 폴더안에 xlsx파일이 여러개 있으므로 날짜와 같은지 폴더이름과 파일이름을 비교한다. 20220105 == 일일보고_20220105.xlsx => [5:-5]
#                                 if ex.endswith('xlsx') and ex[5:-5]==li:
#                                     ## 바로 파일인 애들은 li(파일이름)을 붙이고
#                                     ## 일일마다 폴더가 있다면 날짜이름 폴더 + 파일이름
#                                     file_pathes.append(dir_month+"/"+li+"/"+ex)
#     except Exception as e:
#         print(e)
#     ## 23.11.17 Database 쓰기를 하다가 멈춤현상이 발생했을때 저장하고 다시 가동했을때 그 뒤부터 저장되는 기능 필요

#     # import pandas as pd

#     # df = pd.read_excel(file_pathes[0],sheet_name='일일업무')
#     # pd.set_option('display.max_rows', 500)
#     # pd.set_option('display.max_columns', 500)
#     # pd.set_option('display.width', 1000)
#     # print(df.drop(['Unnamed: 3'],axis=1)
#     db_manager.file_path_to_db(table_name, file_pathes)
#     df = db_manager.read_table()
#     df_1 = df[df['Name']=='방태훈']
#     print(df_1)

from DBManager import DB_Manager
import pandas as pd 
import Works_Analsis as wa
from IPython.core.interactiveshell import InteractiveShell 
InteractiveShell.ast_node_interactivity = "all" # Cell의 모든 반환값 출력


pd.options.display.max_rows = 10000

columns = ['Date','1','2','3','4','5','6','7','8','9','10','11','CODE']

name = '김범석 '

### 엑셀 쓰기 기능 ###
df = pd.DataFrame()
insa = pd.DataFrame(columns=columns)
db_manager = DB_Manager()
df = db_manager.read_table()
df_1 = df[df['Name']==name]

import re
for row in df_1.iterrows():
    works = row[1]['Employee_DIV']
    index_li = []
    excel_write_li = []
    dd , d = wa.get_juya_indexes(works)
    works_list = wa.get_codes_indexes(works, dd, d)
    ## final_list에는 ['주간','작업','호기','등','주간'...] 와 같이 자료가 배치 되어 있기때문에 주간과 주간 사이 주간과 야간사이 등의 인덱스를 리스트화한다
    # 그 다음 그 인덱스 사이의 작업들을 엑셀에 써준다.  
    if len(works_list)>0:
        index = 0
        for li in works_list:
            if li == "주간" or li == "야근" or li == "연장" or li == "야간":
                index_li.append(index)
            index+=1

    final_list = []
    for i in range(len(index_li)):
        if(i>0):
            for j in range(index_li[i-1], index_li[i]):
                # print(works_list[j])
                final_list.append(works_list[j])
                # 한줄씩 리스트를 나눈다. 
            columns_count = 14 - len(final_list)#df columns 갯수에서 빼서 columns갯수를 추가한다. 총 Columns의 갯수 0부터 13 14개
            if(columns_count>0):
                final_list.insert(0, row[1]['Date'])
                final_list.insert(1, row[1]['Name']) 
                for co in range(3,columns_count): # 날짜, 이름, 주간은 그대로 두고 그 다음부터 빈 곳 추가
                    final_list.insert(co, '')
                print(final_list)
                insa.loc[len(insa)] = final_list
                final_list.clear()
            # print("------끝--------") # <- 여기에 엑셀 쓰는 코드
        # 마지막 작업을 추출하기 위해 마지막은 따로 처리
        if i == len(index_li)-1:
            for k in range(index_li[i], len(works_list)):
                # print(works_list[j])
                final_list.append(works_list[k])
                # 한줄씩 리스트를 나눈다. 
            columns_count = 14 - len(final_list)#df columns 갯수에서 빼서 columns갯수를 추가한다. 기본 columns을 넉넉히 만들어서 대비(CAD)
            if(columns_count>0):
                final_list.insert(0, row[1]['Date'])
                final_list.insert(1, row[1]['Name']) 
                for co in range(3,columns_count):
                    final_list.insert(co, '')
                print(final_list)
                insa.loc[len(insa)] = final_list
                final_list.clear()
    # print(insa)
            # print("------끝--------") # <- 여기에 엑셀 쓰는 코드
        # 마지막에 엑셀쓰기는 어떻게 할지 고민
    

        # 이 알고리즘은 한줄에 작업 하나인걸 가만해서 진행. 
        # 작업 리스트에서 0번째 1번째에 날짜와 이름을 넣어주고 있음.
        # if type(li) == list:
        #     if len(li) > 4:
        #         new_li = []
        #         for j in range(0,int(len(li)/4)):
        #             new_li = li[j*4:(j*4)+4]
        #             new_li.insert(0, row[1]['Date'])
        #             new_li.insert(1, row[1]['Name'])
        #             new_li.insert(6, "")
        #             insa.loc[i+j] = new_li
        #         i+=len(li)/4 # 야근이 있으면 두 칸씩 써지기 때문에 2개씩 만약 12개면 3개로 해야한다.
        #     elif len(li) == 4:
        #         li.insert(0, row[1]['Date'])
        #         li.insert(1, row[1]['Name'])
        #         li.insert(6, "")
        #         insa.loc[i] = li
        #         i+=1
        #     else:
        #         li.insert(0, row[1]['Date'])
        #         li.insert(1, row[1]['Name'])
        #         li.insert(2, "")
        #         li.insert(3, "")
        #         li.insert(4, "")
        #         li.insert(5, "")
        #         li.insert(6, li)
        #         # insa.loc[i] = li
        #         i+=1

        #     if type(li) == int:
        #         li.insert(0, row[1]['Date'])
        #         li.insert(1, row[1]['Name'])
        #         li.insert(2, "")
        #         li.insert(3, "")
        #         li.insert(4, "")
        #         li.insert(5, "")
        #         li.insert(6, li)
        #         insa.loc[i] = li
        #         i+=1
        # if len(li) > 4:
        #     new_li = []
        #     for j in range(len(li)):
        #         if j % 4 == 0:
                    
insa.to_excel(f'{name}.xlsx')
    # if type(li) == 'list':
    #     print(li)
    # if type(li) == 'int':
    #     print(li)

