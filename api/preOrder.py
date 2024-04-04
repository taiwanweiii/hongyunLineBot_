from flask import Flask, request, jsonify,Blueprint
from classes.line import *
from classes.db import *
import re
import copy
import ast


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
    from main import getIsProject 

    if apiKey and apiKey == 'mctech' :
        memberDB=MYSQLDB('member')
        if request.method=='GET' and page=='sendMessage':
            #使用者電話
            userPhone=''
            #產品名稱
            productsNamesList=[]
            from main import getIsProject ,posDB
            posOrderlDb=posDB('orders')
            posMemberlDb=posDB('customers')

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
                target=orderData.get('target')

                customersDataList=posMemberlDb.dynamicTableSearch({'id':target,})

                allBalance=allPrice-allPay
                liffID,configsSearchDBProjectList,LineToken,ballRollNumber,searchBallRollfillterTrue,projectDetails,projectList,projectNameList,projectsActiveList,projectsDayList,projectsintervalList,publicBlackTimeList,projectsoffsetList,projectsblockTimeList,projectSnumberOfAppointmentsList,projectGroupReserveStatusList,projectGroupNameList=getIsProject(companyPhone)

                line=LineToken
                template = copy.deepcopy(line.flexTemplate('posOrderMessage'))
                ErrorMessage=''
                if len(customersDataList)==1:
                    try:
                        customersDataList=customersDataList[0]
                        userPhone=customersDataList.get('phone') 
                        userPhone=re.sub(r'\D', '', userPhone)

                        memberData=memberDB.dynamicTableSearch({'company':companyPhone,'phone':userPhone})
                        if memberData:
                            memberData=memberData[0]
                        else:
                            ErrorMessage='Line無會員'
                    except ValueError:
                        print("memberList 無法將變量轉換為字典")
                else:
                    ErrorMessage='Line重複會員或無會員'
                if not isinstance(contentList, dict):
                    try:
                        contentList = json.loads(contentList)
                        productsDataList=contentList.get('products')
                        productsNamesList = [item['name'] for item in productsDataList]
                        countList = [item['count'] for item in productsDataList]
                        productPrice=[item['price'] for item in productsDataList]
                        countxProductPrice = [x * y for x, y in zip(countList, productPrice)]
                        productRemixPrice = {name: price for name, price in zip(productsNamesList, countxProductPrice)}
                        sorted_productRemixPrice = {k: v for k, v in sorted(productRemixPrice.items(), key=lambda item: item[1], reverse=True)}

                    except ValueError:
                        print("contentList 無法將變量轉換為字典")
                else:
                    productsDataList=contentList.get('products')
                    productsNamesList = [item['name'] for item in productsDataList]

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
                        for name in (sorted_productRemixPrice):
                            if sorted_productRemixPrice[name] >=0:
                                templateAdd['contents'][0]['text']=name
                                templateAdd['contents'][1]['text']=f'{sorted_productRemixPrice[name]}$'
                                template['body']['contents'][0]['contents'].append(copy.deepcopy(templateAdd))
                            if sorted_productRemixPrice[name] <0:
                                templateAdd['contents'][0]['text']='折扣'
                                templateAdd['contents'][1]['text']=f'({sorted_productRemixPrice[name]})$'
                                template['body']['contents'][0]['contents'].append(copy.deepcopy(templateAdd))
                        line.pushdoubleMessageTextReplyFlex(memberData['userId'],'若有疑問請致電告知\n☎️:0919102803',template,'簽帳單')

                    case "preOrder" if not ErrorMessage:
                        templateAdd=copy.deepcopy(template['body']['contents'][0]['contents'][0])
                        templateMoney=copy.deepcopy(template['body']['contents'][2])
                        template['body']['contents'][0]['contents']=[]
                        template['body']['contents'][2]['contents'][0]['text']=f'總金額'
                        template['body']['contents'][2]['contents'][1]['text']=f'{allPrice}'

                        templateMoney['contents'][0]['text']='已付款金額'
                        templateMoney['contents'][1]['text']=f'(-{allPay})'
                        template['body']['contents'].append(copy.deepcopy(templateMoney))

                        templateMoney['contents'][0]['text']='剩餘未支付金額'
                        templateMoney['contents'][1]['text']=f'{allBalance}'
                        template['body']['contents'].append(copy.deepcopy(templateMoney))

                        template['header']['contents'][0]['text']='預約單'
                        for name in (sorted_productRemixPrice):
                            if sorted_productRemixPrice[name] >=0:
                                templateAdd['contents'][0]['text']=name
                                templateAdd['contents'][1]['text']=f'{sorted_productRemixPrice[name]}$'
                                template['body']['contents'][0]['contents'].append(copy.deepcopy(templateAdd))
                            elif sorted_productRemixPrice[name]<0:
                                templateAdd['contents'][0]['text']='折扣'
                                templateAdd['contents'][1]['text']=f'({sorted_productRemixPrice[name]})$'
                                template['body']['contents'][0]['contents'].append(copy.deepcopy(templateAdd))
                        line.pushdoubleMessageTextReplyFlex(memberData['userId'],'若有疑問請致電告知\n☎️:0919102803',template,'預定單')
                        print('--countxProductPrice---')
                        print(countxProductPrice)
                        print(productsNamesList)
                        print('--countxProductPrice---')


                    case "delCharge" if not ErrorMessage:
                        templateAdd=copy.deepcopy(template['body']['contents'][0]['contents'][0])
                        templateMoney=copy.deepcopy(template['body']['contents'][2])
                        template['body']['contents'][0]['contents']=[]
                        template['body']['contents'][2]['contents'][0]['text']=f'總金額'
                        template['body']['contents'][2]['contents'][1]['text']=f'{allPrice}'

                        template['header']['contents'][0]['text']='刪除簽帳單'
                        for name in (sorted_productRemixPrice):
                            if sorted_productRemixPrice[name] >=0:
                                templateAdd['contents'][0]['text']=name
                                templateAdd['contents'][1]['text']=f'{sorted_productRemixPrice[name]}$'
                                template['body']['contents'][0]['contents'].append(copy.deepcopy(templateAdd))
                            if sorted_productRemixPrice[name] <0:
                                templateAdd['contents'][0]['text']='折扣'
                                templateAdd['contents'][1]['text']=f'({sorted_productRemixPrice[name]})$'
                                template['body']['contents'][0]['contents'].append(copy.deepcopy(templateAdd))
                        line.pushdoubleMessageTextReplyFlex(memberData['userId'],'若有疑問請致電告知\n☎️:0919102803',template,'刪除簽帳單')
                    case "reserveCheckout" if not ErrorMessage:
                        productNameList=[]
                        for index,item in enumerate(countxProductPrice):
                            if item>=1:
                                productNameList.append(productsNamesList[index])
                        line.pushMessage(memberData['userId'],f'您預定的 {productNameList} 商品已到貨，請記得來店取貨，謝謝😆。')
                    case _:
                        return ErrorMessage


            return 'ok'
        # if request.method == 'GET' and page=='reserveCheckout':
        #     companyPhone=request.args.get('companyPhone')
        #     orderId=request.args.get('orderId')
        #     userPhone=request.args.get('userPhone')
        elif request.method=='GET' and page=='sendMessageApi':
            userId=request.args.get('userId')
            companyPhone=request.args.get('companyPhone')
            message=request.args.get('message')

            if isinstance(companyPhone, str) and companyPhone[0] == '"':
                companyPhone = companyPhone.strip('"')

            print('----companyPhone----')
            print(companyPhone)
            print(type(companyPhone))
            print(companyPhone[0])
            liffID,configsSearchDBProjectList,LineToken,ballRollNumber,searchBallRollfillterTrue,projectDetails,projectList,projectNameList,projectsActiveList,projectsDayList,projectsintervalList,publicBlackTimeList,projectsoffsetList,projectsblockTimeList,projectSnumberOfAppointmentsList,projectGroupReserveStatusList,projectGroupNameList=getIsProject(companyPhone)
            line=LineToken
            userIdObj = ast.literal_eval(userId)
            message = ast.literal_eval(message)
            userIdList = {'successUserId': [], 'errorUserId': []}

            for index, user_id in enumerate(userIdObj):
                try:
                    line.pushMessage(user_id, message[index])
                    userIdList['successUserId'].append(user_id)
                except Exception as e:
                    print(f"处理用户 {user_id} 时出现异常：{e}")
                    userIdList['errorUserId'].append(user_id)
                    pass  # 在捕获到异常后继续执行下一个迭代
            return jsonify(userIdList)


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
            # from main import getIsProject 
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
