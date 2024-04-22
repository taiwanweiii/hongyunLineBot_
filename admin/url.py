url="https://hongyun-line.mctech.tw/"
liff='https://liff.line.me/'
# liff_id='2002260026-2eer414W'
#培訓專區
def training(liff_id):
    trainingValue=[url+'houngyungroup',url+'houngyunpk',liff+liff_id+'?url=userdata',liff+liff_id+'?url=searchuserdata']
    return trainingValue
#球場
def courtReserve(liff_id):
    courtReserveValue=liff+liff_id+'?url=reservecourt&courtplace='
    return courtReserveValue