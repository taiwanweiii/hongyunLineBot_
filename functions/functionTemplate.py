from linebot.models import QuickReplyButton,MessageAction,QuickReply,TextSendMessage,VideoSendMessage,PostbackAction
# def buttonTemplate(button,sendText):
# 	for i in range(len(button)):
# 		QuickReplyButton(action=MessageAction(label=button[i], text=sendText[i] )),

# 	flex_message=TextSendMessage(text="請選擇要預約項目",
# 		quick_reply=QuickReply(items=[
# 				QuickReplyButton(action=MessageAction(label=button[i], text=sendText[i] )),
# 			# QuickReplyButton(action=MessageAction(label=button[1], text=sendText[1] )),
# 			# QuickReplyButton(action=MessageAction(label=button[2], text=sendText[2] )),
# 			# QuickReplyButton(action=MessageAction(label=button[3], text=sendText[3] )),
# 			# QuickReplyButton(action=MessageAction(label=button[4], text=sendText[4] )),
# 			# QuickReplyButton(action=MessageAction(label=button[5], text=sendText[5] ))
# 		]))
# 	return(flex_message)

def buttonTemplate(button, sendText,sendMessages="請選擇要預約項目"):
    quick_reply_items = [
        QuickReplyButton(action=MessageAction(label=button[i], text=sendText[i])) for i in range(len(button))
    ]

    flex_message = TextSendMessage(text=sendMessages, quick_reply=QuickReply(items=quick_reply_items))
    return flex_message

def postUnderTemplate(underbuttonList,dataList,officialText="officialText的文字"):
    quick_reply_items = [
        QuickReplyButton(action=PostbackAction(label=underbuttonList[i], data=dataList[i], )) for i in range(len(dataList))


    ]
    flex_message = TextSendMessage(text=officialText, quick_reply=QuickReply(items=quick_reply_items))
    return flex_message

def videoTemplate(videoURL,pictureURL):
	flex_message=VideoSendMessage(
		original_content_url=videoURL,
		preview_image_url=pictureURL
	)
	return(flex_message)

