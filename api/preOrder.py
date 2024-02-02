from flask import Flask, request, jsonify,Blueprint
from classes.line import *
from classes.db import *
import re
import copy


data={"Name":123,'Number':1}

def getLine(companyPhone='0912345678'):
    pass

PreOrderBlueprint = Blueprint('preOrder', __name__)
'''
{
    "companyPhone":"123",
    "userPhone":"456",
    "project":"項目"
}
'''
# Line
@PreOrderBlueprint.route('/<page>', methods=['POST','GET'])
def preOrderSendMessage(page):
    apiKey=request.headers.get('Key')
    requiredKeys = ['userPhone', 'project', 'money', 'companyPhone', 'title']

    if apiKey and apiKey == 'mctech' :
        memberDB=MYSQLDB('member')
        if request.method=='GET' and page=='preOrderSendMessage':
            #使用者電話
            userPhone=''
            #產品名稱
            productsNamesList=[]
            from main import getIsProject ,posDB
            posOrderlDb=posDB('orders')
            companyPhone=request.args.get('companyPhone')
            # userid=request.args.get('userId')
            orderId=request.args.get('orderId')
            titleType=request.args.get('type')

            orderData=(posOrderlDb.TableOneSearch('id',orderId))

            if (orderData):
                orderData=orderData[0]
                contentList = orderData.get('content')
                memberList = orderData.get('target_content')
                allPrice = orderData.get('price')
                allPay=orderData.get('revenue')
                allBalance=allPrice-allPay
                configsSearchDBProjectList,LineToken,ballRollNumber,searchBallRollfillterTrue,projectDetails,projectList,projectNameList,projectsActiveList,projectsDayList,projectsintervalList,publicBlackTimeList,projectsoffsetList,projectsblockTimeList,projectSnumberOfAppointmentsList,projectGroupReserveStatusList,projectGroupNameList=getIsProject(companyPhone)
                line=LineToken
                template = copy.deepcopy(line.flexTemplate('posOrderMessage'))
                ErrorMessage=''
                if not isinstance(memberList, dict):
                    try:
                        memberList = json.loads(memberList)
                        userPhone=memberList.get('phone') 
                        userPhone=re.sub(r'\D', '', userPhone)
                        memberData=memberDB.dynamicTableSearch({'company':companyPhone,'phone':userPhone})

                        if memberData:
                            memberData=memberData[0]
                        else:
                            ErrorMessage='Line無會員'
                    except ValueError:
                        print("memberList 無法將變量轉換為字典")
                else:
                    userPhone=memberList.get('phone') 
                    userPhone=re.sub(r'\D', '', userPhone)
                if not isinstance(contentList, dict):
                    try:
                        contentList = json.loads(contentList)
                        productsDataList=contentList.get('products')
                        productsNamesList = [item['name'] for item in productsDataList]
                        countList = [item['count'] for item in productsDataList]
                        productPrice=[item['price'] for item in productsDataList]
                        countxProductPrice = [x * y for x, y in zip(countList, productPrice)]

 
                    except ValueError:
                        print("contentList 無法將變量轉換為字典")
                else:
                    productsDataList=contentList.get('products')
                    productsNamesList = [item['name'] for item in productsDataList]
                print('----ErrorMessage-----')
                print(bool(ErrorMessage))
                match titleType:
                    case "charge" if not ErrorMessage:
                        templateAdd=copy.deepcopy(template['body']['contents'][0]['contents'][0])
                        templateMoney=copy.deepcopy(template['body']['contents'][2])

                        template['body']['contents'][0]['contents']=[]
                        template['body']['contents'][2]['contents'][1]['text']=f'{allPrice}'
                        template['header']['contents'][0]['text']='簽帳單'

                        templateMoney['contents'][0]['text']='已付款金額'
                        templateMoney['contents'][1]['text']=f'-({allPay})'
                        template['body']['contents'].append(copy.deepcopy(templateMoney))

                        templateMoney['contents'][0]['text']='剩餘未支付金額'
                        templateMoney['contents'][1]['text']=f'{allBalance}'
                        template['body']['contents'].append(copy.deepcopy(templateMoney))
                        for index,item in enumerate(countxProductPrice):
                            if item >=0:
                                templateAdd['contents'][0]['text']=productsNamesList[index]
                                templateAdd['contents'][1]['text']=f'{item}$'
                                template['body']['contents'][0]['contents'].append(copy.deepcopy(templateAdd))
                            elif item<0:
                                templateAdd['contents'][0]['text']='折扣'
                                templateAdd['contents'][1]['text']=f'-{item}$'
                                template['body']['contents'][0]['contents'].append(copy.deepcopy(templateAdd))
                        line.pushdoubleMessageTextReplyFlex(memberData['userId'],'若有疑問請致電告知\n☎️:0919102803',template,'簽帳單')

                    case "preOrder" if not ErrorMessage:
                        templateAdd=copy.deepcopy(template['body']['contents'][0]['contents'][0])
                        templateMoney=copy.deepcopy(template['body']['contents'][2])
                        template['body']['contents'][0]['contents']=[]
                        template['body']['contents'][2]['contents'][0]['text']=f'總金額'
                        template['body']['contents'][2]['contents'][1]['text']=f'{allPrice}'

                        templateMoney['contents'][0]['text']='已付款金額'
                        templateMoney['contents'][1]['text']=f'-({allPay})'
                        template['body']['contents'].append(copy.deepcopy(templateMoney))

                        templateMoney['contents'][0]['text']='剩餘未支付金額'
                        templateMoney['contents'][1]['text']=f'{allBalance}'
                        template['body']['contents'].append(copy.deepcopy(templateMoney))

                        template['header']['contents'][0]['text']='預約單'
                        for index,item in enumerate(countxProductPrice):
                            if item >=0:
                                templateAdd['contents'][0]['text']=productsNamesList[index]
                                templateAdd['contents'][1]['text']=f'{item}$'
                                template['body']['contents'][0]['contents'].append(copy.deepcopy(templateAdd))
                            elif item<0:
                                templateAdd['contents'][0]['text']='折扣'
                                templateAdd['contents'][1]['text']=f'-{item}$'
                                template['body']['contents'][0]['contents'].append(copy.deepcopy(templateAdd))
                        line.pushdoubleMessageTextReplyFlex(memberData['userId'],'若有疑問請致電告知\n☎️:0919102803',template,'簽帳單')

                    case "delCharge" if not ErrorMessage:
                        templateAdd=copy.deepcopy(template['body']['contents'][0]['contents'][0])
                        templateMoney=copy.deepcopy(template['body']['contents'][2])
                        template['body']['contents'][0]['contents']=[]
                        template['body']['contents'][2]['contents'][0]['text']=f'總金額'
                        template['body']['contents'][2]['contents'][1]['text']=f'{allPrice}'

                        template['header']['contents'][0]['text']='刪除簽帳單'
                        for index,item in enumerate(countxProductPrice):
                            if item >=0:
                                templateAdd['contents'][0]['text']=productsNamesList[index]
                                templateAdd['contents'][1]['text']=f'{item}$'
                                template['body']['contents'][0]['contents'].append(copy.deepcopy(templateAdd))
                            elif item<0:
                                templateAdd['contents'][0]['text']='折扣'
                                templateAdd['contents'][1]['text']=f'-{item}$'
                                template['body']['contents'][0]['contents'].append(copy.deepcopy(templateAdd))
                        line.pushdoubleMessageTextReplyFlex(memberData['userId'],'若有疑問請致電告知\n☎️:0919102803',template,'簽帳單')
                    case _:
                        return ErrorMessage


            return 'ok'


        elif request.method=='POST' and page=='preOrderSendMessage' and all(key in value for key in requiredKeys):
            value=request.get_json()
                
            userPhone=value['userPhone']
            project=value['project']
            money=value['money']
            companyPhone=value['companyPhone']
            title=value['title']
            memberData=memberDB.dynamicTableSearch({'company':companyPhone,'phone':userPhone})
            if memberData:
                memberData=memberData[0]
                print(memberData)
            from main import getIsProject 
            configsSearchDBProjectList,LineToken,ballRollNumber,searchBallRollfillterTrue,projectDetails,projectList,projectNameList,projectsActiveList,projectsDayList,projectsintervalList,publicBlackTimeList,projectsoffsetList,projectsblockTimeList,projectSnumberOfAppointmentsList,projectGroupReserveStatusList,projectGroupNameList=getIsProject(companyPhone)
            line=LineToken
            if title=="預約單":
                title=title+'\n項目:'
            elif title=='簽帳單':
                title=title+'\n結帳:'
            elif title=='刪除簽帳單':
                title=title+'\n項目:'
            line.pushMessage(memberData['userId'],
                            f'''{title}{project}\n金額:{money}$\n若有疑問請致電告知\n☎️:0919102803''')
            return jsonify({'reture':'ok'})
        else:
            return 'no member'
    else:
        return({"error":"Invalid API key"}),401
