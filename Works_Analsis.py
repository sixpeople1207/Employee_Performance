import re 
from DBManager import DB_Manager
import pandas as pd 


def get_juya_indexes(jackup):
    try:
        indexes = []
        works_type = ['','']
        works_type_gubun = ""
        ju_index = re.search('주간', jackup)
        if ju_index != None:
            works_type[0]='주간'
            indexes.append(ju_index.start())
            # print(f"주간 위치: {ju_index.start()}")
        yunjang_index = re.search('연장', jackup)
        if yunjang_index != None:  
            works_type[1]='연장'  
            indexes.append(yunjang_index.start())
            # print(f"연장 위치: {yunjang_index.start()}")
        yagun_index = re.search('야근', jackup)
        if yagun_index != None:
            works_type[1]='야근'  
            indexes.append(yagun_index.start())
            # print(f"야근 위치: {yagun_index.start()}")
        yagun_index = re.search('야간', jackup)
        if yagun_index != None:
            works_type[1]='야간'  
            indexes.append(yagun_index.start())
            # print(f"야간 위치: {yagun_index.start()}")
            
        # type [주간,야근]:1, [주간,연장]:2, [,야근]:3, [,연장]:4, [,]:5
        if works_type[0] == '주간' and works_type[1] == '야근':
            works_type_gubun = "야근"
        elif works_type[0] == '주간' and works_type[1] == '연장':
            works_type_gubun = "연장"
        elif works_type[0] == '주간' and works_type[1] == '야간':
            works_type_gubun = "연장"
        elif works_type[0] == '' and works_type[1] == '야근': ##type_1에 주간을 넣어준다. 
            jackup = '주간'+jackup
            indexes.insert(0,0)
            works_type_gubun = "야근"
        elif works_type[0] == '' and works_type[1] == '연장':
            jackup = '주간'+jackup
            indexes.insert(0,0)
            works_type_gubun = "연장"
        elif works_type[0] == '' and works_type[1] == '': ##type_1에 주간만 넣어준다.
            jackup = '주간'+jackup
            indexes.insert(0,0)
            indexes.append(len(jackup))
            works_type_gubun = "야근" ## 야근 연장 구분이 없기 때문에 그냥 STR맨 끝까지 
        return indexes, works_type_gubun
    except Exception as e:
        print(e)

    ## Ju = 1 / Yagun = 0.25 / Yunjang = 0.5 ##
def get_codes_indexes(jackup, juya_indexes, works_type_gubun):
    YAGUN = False
    YUNJANG = False
    ju_index = juya_indexes[0]
    ya_index=0
    if works_type_gubun == "야근":
        ya_index = juya_indexes[1]
        YAGUN = True
    elif works_type_gubun == "연장":
        ya_index = juya_indexes[1]
        YUNJANG = True
    
    data = [] # works_mat_object에넣기 전 리스트
    util_li = [] # 작업에 유틸 추가
    works_mat_object = []
    works_util_object = []
    exception_li = [] ## 예외되는 작업 리스트들은 여기에 저장.
    #code = re.compile('(\d{1}\w{4}\d{3})(.*?)|(\d{1}\w{4}\d{3})|(\d{1}\w{3}\d{4})|(\w{4}\d{4})|(\w{5}\d{3})').findall(jackup)
    mat = re.finditer('(\d{1}\w{4}\d{3})|(\d{1}\w{3}\d{4})|(\w{4}\d{4})|(\w{5}\d{3})', jackup)

    contius_codes = re.sub("\s","",jackup)
    is_contius_codes = re.finditer(',\d{4}',contius_codes)
    code_indexes = list(iter(mat))

## 코드를 찾지 못한다면 
    if len(code_indexes) == 0:
        exception_li.append(jackup)
        print("코드를 찾지 못했습니다.")
    
    works = ['설계','TRAY','보강대','간섭','이슈','협의','정보추출','3차 배관'] ## => 설계
    works_B = ['도면출도','도면작업'] ## 도면 정리 제외
    works_C = ['업데이트','REV'] ## => 업데이트
    works_Util = ['GAS','PCW','DR','EXH','VAC','SCR','BYP','TRAY']

# 작업내용리스트를 돌면서 매칭된 re.Match object를 리스트로 가져온다. 단 두개 이상일때는 별도의 작업필요.
    for work in works:
        index = re.finditer(work,jackup)
        data.append(list(iter(index)))
    for B in works_B:
        index = re.finditer(B,jackup)
        data.append(list(iter(index)))
    for C in works_C:
        index = re.finditer(C,jackup)
        data.append(list(iter(index)))

    # re.Match object이(찾은 결과가) 2개 이상일때는 한번더 배열에 넣어준다.
    for i in range(len(data)):
        if len(data[i]) == 1:
            works_mat_object.append(data[i][0])
        elif len(data[i]) > 1:
            for j in range(len(data[i])):
                ## data[i]가 2개 이상일 때는 2차원 배열이기 때문에 2번째 배열을 변경해준다.
                works_mat_object.append(data[i][j])

     #23.11.20추가 유체 정보 가져오기
    for D in works_Util:
        index = re.finditer(D,jackup)
        util_li.append(list(iter(index)))

     # re.Match object이(찾은 결과가) 2개 이상일때는 한번더 배열에 넣어준다.
    for i in range(len(util_li)):
        if len(util_li[i]) == 1:
            works_util_object.append(util_li[i][0])
        elif len(util_li[i]) > 1:
            for j in range(len(util_li[i])):
                ## data[i]가 2개 이상일 때는 2차원 배열이기 때문에 2번째 배열을 변경해준다.
                works_util_object.append(util_li[i][j])
    
    # Sorted 정렬로 순서대로 정렬해서 위치값이 작은 순서대로 사용.
    works_mat_object=sorted(works_mat_object, key=lambda x:x.start())
    works_util_object=sorted(works_util_object, key=lambda x:x.start())
    
    # 주간과 야근 사이에 호기,, 작업이 되는지. 작업 되에 호기가 있는지 판단 
    # 야근 뒤에 호기와 작업이 있는가? 검수하는 코드
    codes = []
    mats = []
    for code in code_indexes:
        codes.append(code.start())
    for mat in works_mat_object:
        mats.append(mat.start())

    codes.sort()
    mats.sort()
    ok_count = 0

    ## mats는 작업의 수 codes수와 매칭하려고 하니 당연히 되지 않는다. 한 코드에 한 개이상의 작업이 매칭되는 경우도 발생.
 
    for k in range(len(mats)):
        if k-1 < 0:
            before = 0
            current = mats[k]
        else:
            before = mats[k-1]
            current = mats[k]

        for co in codes:
            if co > before and co < current and co < ya_index:
                ok_count+=1
            else:
                if co > ya_index and co < current and co > before: ## co > before 코드 추가 23.11.21 -> 아직 연장을 8개나 잡음.. ! 
                    ok_count+=1
       
    if ok_count != len(codes):
        print(ok_count)
        print(len(codes))
        print("예외처리입니다.")

    """
        분석 타입. 
            호기 호기 작업, 알수없음 
            호기 작업 , 호기 작업 + 유틸 추가(23.11.22)
            작업 호기 호기 
            알수없음 알수없음 호기 등등
            작업 위치를 두개의 인덱스로 판단한다. ---호기--작업1 ---호기--작업2  일때 첫 작업일때는 작업1 보다 작을때만 가져오기 위해 
        예외 처리.
            1. 만약 호기가 before에 없다면 작업부터 다음 작업까지 검색해야한다.  <-----
            2. before와 after라는 변수로 함축하여 값을 정의한다. 그냥 바로 인덱스로 비교하면 조건이 까다롭다. 
            3. 이렇게 하면 작업과 작업 사이의 객체를 모두 가져올 수 있다. 하지만 호기가 같을 때 작업이 같을 때는 공종으로 비교한다. 
            4. 공종 비교 TAT 정도만 남았다 작업이 .. 이제 어느정도 분석할 수 있게 되었다. 
            5. 여기서 타입을 구분할 수 있을 것 같다. 코드와 작업의 관계를 파악할 수 있다. 만약 코드가 없다면도 파악가능! 
            6. 코드는 무조건 1개 이상이기 때문에 여기서 타입을 판단한다. 판단 할 때는 첫 작업과 호기의 관계 두개 이상이면 호기의 관계를 파악한다. 
            7. 코드의 갯수로 TAT를 판단 한다. (주간이면 1/호기)
    """
    # 주간에 작업한 호기갯수와 야근에 작업한 호기를 나눈다. 
    ju_count = 0
    ya_count = 0 

    for code in code_indexes:
        if ju_index < code.start() and ya_index > code.start():
            ju_count+=1
        if ya_index < code.start():
            ya_count+=1

    # TAT를 구한다. 
    # TAT는 주간에 한 호기갯수와 주간 TAT 1을 나누 값.
    # JU_TAT = 1/ju_count
    # 야근 연장 TAT는 야간에 한 호기 갯수와 야근 0.25시간 연장 0.5(반일)을 나눈 값.
    if YAGUN == True and ya_count > 0:
        YA_TAT = 0.25/ya_count
    elif YUNJANG == True and ya_count > 0:
        YA_TAT = 0.5/ya_count

    # 마지막 반환리스트에 값을 하나씩 넣어준다. 야간 야근포함.
    # 주간 야근 사이 before 와 current는 작업을 구분하고, 그 작업 사이에 호기를 잡아낸다. 다음은 야근 이후의 작업을 잡아낸다. 없으면 버림. 
    final_list = []

    ## works_mat_object 작업 리스트와 작업의 Index를 가지고 있다.
    ## 아래 코드는 작업과 코드의 상관관계를 구하는 식인데.. 코드가 앞에 가는 경우도 있고 뒤에 가는 경우도 있기 때문 일것이란 생각. 23.11.20
    ## 그래서 먼저 작업이 야간앞인지 확인하고 그 다음 코드와의위치를 판단.

    ## 이렇게 복잡하게 진행할게 아니라 정규식으로 그냥 판단해도 되지 않을까란 생각 23.11.20
    ## 설비와 설비코드 위치를 잘라서 그 내부에서 정규식을 한번 더 적용하는 것이다. 
    ## 에를 들어 주간과 야간을 한번 자르고, 주간에서 설비와 설비를 자르고 그 다음 작업, 유체로 한줄 쓰기, 그 다음 그 다음 적용. 
    for j in range(len(works_mat_object)):
        if j-1 < 0: 
            before = 0
            current = works_mat_object[j].start()
            # 야간보다 설계나 작업의 인덱스가 크면 야근의 위치부터 기준
        else:
            before = works_mat_object[j-1].start()
            current = works_mat_object[j].start()

        # 주간 작업을 나눈다.
        text_judo = []
        for code in code_indexes:
            # print(before," ", code.start()," ", current)
            if code.start() > before and code.start() < current:
                # print(code)
                if code.start() < ya_index:
                    final_list.append("주간")
                elif code.start() > ya_index:
                    # print(f'인덱스 : {code.start()} 설비 명: {code.group()}')
                    if YAGUN == True:
                        final_list.append("야근")
                    elif YUNJANG == True:
                        final_list.append("연장")
                # 호기와 설계작업 사이 유틸정보를 최종 리스트에 적용.
                for util in works_util_object:
                    if util.start() < current and util.start() > before:
                        final_list.append(util.group())
                final_list.append(works_mat_object[j].group()) # 작업 쓰기
                final_list.append(code.group()) # 코드
                text_judo.append(code.group()) # ?무슨 항목인지
                # final_list.append(YA_TAT) # TAT
    return final_list

        
def continu_codes(work_text):
    work_text = work_text.replace(" ","")
    continu_codes_before_codes = re.finditer('\d{1}\w{4}\d{3},\d{4}',work_text)
    continu_codes = re.sub("\s","",work_text)
    continu_number = re.finditer(',\d{4}',continu_codes)
    final_list = []
    if len(list(iter(continu_number))) > 1:
        print("연속 숫자 모드")
    ya_index = re.finditer("야근",work_text)
    ya_index = list(iter(ya_index))
    ya_index = ya_index[0].start()

    for code in continu_codes_before_codes:
        # print(code)
        # print(ya_index)
        for number in continu_number:
        # 설비코드,호기,호기 일때 야근까지 
            # print("num",number)
            # print("code",code)
            # print("야",ya_index)
            if code.start() < ya_index and code.start() < number.start() and ya_index > number.start():
                ju_new_code = code.group()[:4]+number.group()[1:]
                final_list.append("주간")
                final_list.append(ju_new_code)
                # print("주간 :",ju_new_code)
            if code.start() < number.start() and ya_index < number.start():
                ya_new_code = code.group()[:4]+number.group()[1:]
                # print("야간",ya_new_code)
                final_list.append("야간")
                final_list.append(ya_new_code)
    return final_list