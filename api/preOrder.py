from flask import Flask, request, jsonify,Blueprint
from classes.line import *
from classes.db import *


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
    value=request.get_json()
    requiredKeys = ['userPhone', 'project', 'money', 'companyPhone', 'title']

    if apiKey and apiKey == 'mctech' and all(key in value for key in requiredKeys):
        userPhone=value['userPhone']
        project=value['project']
        money=value['money']
        companyPhone=value['companyPhone']
        title=value['title']
        memberDB=MYSQLDB('member')
        memberData=memberDB.dynamicTableSearch({'company':companyPhone,'phone':userPhone})
        if memberData:
            memberData=memberData[0]
            print(memberData)
            if request.method=='POST' and page=='preOrderSendMessage':
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
