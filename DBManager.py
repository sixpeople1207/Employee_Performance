import sqlite3
import re
import pandas as pd 

class DB_Manager:
    def __init__(self) -> None:
        self.db_path = './DAILY_WORKS.db'
        self.conn = sqlite3.connect(self.db_path)
        self.curs = self.conn.cursor()

    def __del__(self):
        del self 

    def create_table(self, table_name, table_list):
        try:
            sql = f"CREATE TABLE IF NOT EXISTS {table_name}({table_list});"
            self.curs.execute(sql)
            self.conn.commit()
        except sqlite3.Error as e:
            print(e)
    
    def drop_table(self, table_name):
        try:
            sql = f"DROP TABLE {table_name};"
            self.curs.execute(sql)
            self.conn.commit()
        except sqlite3.Error as e:
            print(e)
            
    def delete_rows(self, table_name):
        try:
            sql = f"DELETE FROM {table_name};"
            self.curs.execute(sql)
            self.conn.commit()
        except sqlite3.Error as e:
            print(e)

    def excute_daily_work(self, table_name, date, name, code, employee_DIV, works_DIV, tat):
        f"""
        CREATE TABLE IF NOT EXISTS {table_name}(
        Date datetime,
        Name TEXT,
        Code TEXT,
        Employee_DIV TEXT, 
        Works_DIV TEXT,
        TAT TEXT
        );
        """
        try:
            sql = f"INSERT INTO {table_name} VALUES (?,?,?,?,?,?)"
            self.curs.execute(sql, (date,name,code,employee_DIV,works_DIV,tat))
            self.conn.commit()
        except sqlite3.Error as e:
            print(e)

    def file_path_to_db(self, table_name, file_pathes):
        pd.set_option('display.max_rows', 500)
        pd.set_option('display.max_columns', 500)
        pd.set_option('display.width', 1000)
        for file_path in file_pathes:   
            try:
                df = pd.read_excel(file_path, sheet_name='일일업무')
                ## 필요없는 열을 지워준다.
                ## 열의 갯수를 카운트해서
                for i in range(4,len(df.columns)):
                    df = df.drop(columns=['Unnamed: '+str(i)])

                # 열 이름을 보기 좋게 바꾼다. 
                df = df.rename(columns={'  일일 업무보고서':'날짜','Unnamed: 1':'현장','Unnamed: 2':'이름','Unnamed: 3':'작업'})

                ## 한 열을 날짜로 채워준다. 
                df['날짜'] = df['날짜'].apply(lambda x:file_path[-13:-5]) 
                ## 이름만 추출 한다.
                names = df['이름'].drop_duplicates() 
                ## 정규식으로 이름만 추출한다. 
                for name in names.iteritems():
                    text = re.compile('[가-힣]').findall(str(name[1])) # 첫 번째 값은 행번호 두 번째가 이름임. Series이기 때문에 str형변환
                    if len(text) == 3 or len(text) == 2:
                        ## 정규식으로 이름을 걸러내고(text) 리스트로 사용하기 어려우니 바로 name과 작업내역을 데이터베이스에 넣는다.
                        daily_work = df[df['이름']== str(name[1])]
                        # print(str(name[1]) + " : " + str(daily_work))
                        daily_work = daily_work.drop(columns=['현장'])
                        ## 주간 데이터 한번 (daily_work는 데이터 프레임 2열 존재함. daily_work[''][1]이 내용임.
                        """
                            작업 내역 분할해서 데이터 베이스에 넣고 엑셀로 뽑으면 끝
                        """
                        ## 데이터를 분석해서 일별로 주간 호기 야간 호기 이슈대응, 교육 등을 분석해서 행을 늘린다. 
                        ## for문으로 진행해야할 것 같다. 
                        daily_work
                        self.excute_daily_work(table_name, daily_work['날짜'].to_list()[0], daily_work['이름'].to_list()[0], "nan", daily_work['작업'].to_list()[0],"nan","nan")
                        # db_manager.excute_daily_work(table_name, daily_work['날짜'].to_list()[0], daily_work['이름'].to_list()[0], "nan", daily_work['작업'].to_list()[0],"nan","nan")
                # works = pd.concat([works,df],axis = 1)
            except sqlite3.Error as e:
                print(file_path)
                print(e)
        return 1 ##저장된 열의 갯수 정도 반환
    
    def read_table(self):
        try:
            sql = "SELECT * FROM M15_DAILY_WORKS;"
            df = pd.read_sql(sql,self.conn)
            return df 
        except sqlite3.Error as e:
            print(e)
