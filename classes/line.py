from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage, FlexSendMessage,ImageSendMessage
)
import json

class Line:
    event = None

    def __init__(self, CHANNEL_ACCESS_TOKEN=None, CHANNEL_SECRET=None):
        self.api = LineBotApi(CHANNEL_ACCESS_TOKEN)
        self.webhook = WebhookHandler(CHANNEL_SECRET)

    class Event:
        def __init__(self, event):
            self.event = event
            self.type = event.get('type', None)
            self.uid = event.get('source', {}).get('userId', None)
            self.message = event.get('message', {}).get('text', None)
            self.messageType = event.get('message', {}).get('type', None)
            self.replyToken = event.get('replyToken', None)
            self.timestamp = event.get('timestamp', None)
            # 
            self.postback = event.get('postback', {}).get('data', None)

    def setEvent(self, event): 
        self.event = Line.Event(event)
        return self.event
    
    @staticmethod
    def flexTemplate(filename):
        with open(f"templates/{filename}.json", 'r',encoding="utf-8") as f: data = json.load(f)
        return data

    # reply message functions
    def replyMessage(self, formatText):
        self.api.reply_message(self.event.replyToken, formatText)
    def doubleReplyMessageText(self,text1,text2):
        messages = [
            TextSendMessage(text=f"{text1}"),
            TextSendMessage(text=f"{text2}")
        ]
        self.replyMessage(messages)

    def replyText(self, text):
        self.replyMessage(TextSendMessage(text=text))

    def replyFlex(self, contents, alt_text='-'):
        self.replyMessage(FlexSendMessage(contents=contents, alt_text=alt_text))

    def doubleReplyFlexMessageText(self, text1, flex_contents,alt_text='-'):
        messages = [
            TextSendMessage(text=text1),
            FlexSendMessage(contents=flex_contents,alt_text=alt_text)
        ]
        self.replyMessage(messages)
    def doubleReplyTwoFlex(self,flex_contentsOne,flex_contentsTwo,altTextOne='1',altTextTwo='2'):
        messages = [
            FlexSendMessage(contents=flex_contentsOne,alt_text=altTextOne),
            flex_contentsTwo
        ]
        self.replyMessage(messages)

    def doubleMessageTextReplyFlex(self, text1, flex_contents,alt_text='-'):
        messages = [
            FlexSendMessage(contents=flex_contents,alt_text=alt_text),
            TextSendMessage(text=text1)

            
        ]
        self.replyMessage(messages)

    def replyTextAndImage(self, text, image_url):
        # 回覆文字訊息
        text_message = TextSendMessage(text=text)

        # 回覆圖片訊息
        image_message = ImageSendMessage(
            original_content_url=image_url,
            preview_image_url=image_url
        )

        # 發送回覆訊息
        self.api.reply_message(self.event.replyToken, [text_message, image_message])

    # /reply message functions
    #push Message
    def pushMessage(self,userId,messageText):
        message = TextSendMessage(text=messageText)

        self.api.push_message(userId,messages=message)

    def pushFlexMessage(self,userId,data):
        flex_message = FlexSendMessage(alt_text='-', contents=data)
        self.api.push_message(userId,messages=flex_message)