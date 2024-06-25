import os
import re
import base64
from tqdm import tqdm
from typing import List, Dict
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from .tool import Tool


class MailTool(Tool):
    __VALID_ACTION__ = ["read", "send"]

    def __init__(self, cfg_file: str, default_action: str = "read"):
        description = "Read and send e-mails"
        name = "mail"
        parameters = {
            "action": {
                "type": "string",
                "description": "The action to be performed, read or send",
            },
            "state": {
                "type": "string",
                "description": "The state of the email, all, unread, read, sent",
            },
            "time_between": {
                "type": "array",
                "description": "The time range of the email, such as ['2021/01/01', '2021/01/02']",
            },
            "sender_mail": {
                "type": "string",
                "description": "The sender's email address",
            },
            "only_both": {
                "type": "boolean",
                "description": "Whether to search for both sender and recipient",
            },
            "order_by_time": {
                "type": "string",
                "description": "The order of the email, descend or ascend",
            },
            "include_word": {
                "type": "string",
                "description": "The word to be included in the email",
            },
            "exclude_word": {
                "type": "string",
                "description": "The word to be excluded in the email",
            },
            "MAX_SEARCH_CNT": {
                "type": "integer",
                "description": "The maximum number of emails to search",
            },
            "number": {
                "type": "integer",
                "description": "The number of emails to be returned",
            },
            "recipient_mail": {
                "type": "string",
                "description": "The recipient's email address",
            },
            "subject": {
                "type": "string",
                "description": "The subject of the email",
            },
            "body": {
                "type": "string",
                "description": "The body of the email",
            },
        }
        super(MailTool, self).__init__(description, name, parameters)
        assert (
            default_action.lower() in self.__VALID_ACTION__
        ), f"Action `{default_action}` is not allowed! The valid action is in `{self.__VALID_ACTION__}`"
        self.action = default_action.lower()
        self.credential = self._login(cfg_file)

    def _login(self, cfg_file: str):
        SCOPES = [
            "https://www.googleapis.com/auth/gmail.readonly",
            "https://www.googleapis.com/auth/gmail.send",
        ]
        creds = None
        if os.path.exists("token.json"):
            print("Login Successfully!")
            creds = Credentials.from_authorized_user_file("token.json", SCOPES)
        if not creds or not creds.valid:
            print("Please authorize in an open browser.")
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(cfg_file, SCOPES)
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open("token.json", "w", encoding="utf-8") as token:
                token.write(creds.to_json())
        return creds

    def _read(self, mail_dict: dict):
        credential = self.credential
        state = mail_dict["state"] if "state" in mail_dict else None
        time_between = (
            mail_dict["time_between"] if "time_between" in mail_dict else None
        )
        sender_mail = mail_dict["sender_mail"] if "sender_mail" in mail_dict else None
        only_both = mail_dict["only_both"] if "only_both" in mail_dict else False
        order_by_time = (
            mail_dict["order_by_time"] if "order_by_time" in mail_dict else "descend"
        )
        include_word = (
            mail_dict["include_word"] if "include_word" in mail_dict else None
        )
        exclude_word = (
            mail_dict["exclude_word"] if "exclude_word" in mail_dict else None
        )
        MAX_SEARCH_CNT = (
            mail_dict["MAX_SEARCH_CNT"] if "MAX_SEARCH_CNT" in mail_dict else 50
        )
        number = mail_dict["number"] if "number" in mail_dict else 10
        if state is None:
            state = "all"
        if time_between is not None:
            assert isinstance(time_between, tuple)
            assert len(time_between) == 2
        assert state in ["all", "unread", "read", "sent"]
        if only_both:
            assert sender_mail is not None
        if sender_mail is not None:
            assert isinstance(sender_mail, str)
        assert credential
        assert order_by_time in ["descend", "ascend"]

        def generate_query():
            query = ""
            if state in ["unread", "read"]:
                query = f"is:{state}"
            if state in ["sent"]:
                query = f"in:{state}"
            if only_both:
                query = f"{query} from:{sender_mail} OR to:{sender_mail}"
            if sender_mail is not None and not only_both:
                query = f"{query} from:({sender_mail})"
            if include_word is not None:
                query = f"{query} {include_word}"
            if exclude_word is not None:
                query = f"{query} -{exclude_word}"
            if time_between is not None:
                TIME_FORMAT = "%Y/%m/%d"
                t1, t2 = time_between
                if t1 == "now":
                    t1 = datetime.now().strftime(TIME_FORMAT)
                if t2 == "now":
                    t2 = datetime.now().strftime(TIME_FORMAT)
                if isinstance(t1, str) and isinstance(t2, str):
                    t1 = datetime.strptime(t1, TIME_FORMAT)
                    t2 = datetime.strptime(t2, TIME_FORMAT)
                elif isinstance(t1, str) and isinstance(t2, int):
                    t1 = datetime.strptime(t1, TIME_FORMAT)
                    t2 = t1 + timedelta(days=t2)
                elif isinstance(t1, int) and isinstance(t2, str):
                    t2 = datetime.strptime(t2, TIME_FORMAT)
                    t1 = t2 + timedelta(days=t1)
                else:
                    assert False, "invalid time"
                if t1 > t2:
                    t1, t2 = t2, t1
                query = f"{query} after:{t1.strftime(TIME_FORMAT)} before:{t2.strftime(TIME_FORMAT)}"
            return query.strip()

        def sort_by_time(data: List[Dict]):
            if order_by_time == "descend":
                reverse = True
            else:
                reverse = False
            sorted_data = sorted(
                data,
                key=lambda x: datetime.strptime(x["time"], "%Y-%m-%d %H:%M:%S"),
                reverse=reverse,
            )
            return sorted_data

        try:
            service = build("gmail", "v1", credentials=credential)
            results = (
                service.users()
                .messages()
                .list(userId="me", labelIds=["INBOX"], q=generate_query())
                .execute()
            )

            messages = results.get("messages", [])
            email_data = list()

            if not messages:
                print("No eligible emails.")
                return None
            else:
                pbar = tqdm(total=min(MAX_SEARCH_CNT, len(messages)))
                for cnt, message in enumerate(messages):
                    pbar.update(1)
                    if cnt >= MAX_SEARCH_CNT:
                        break
                    msg = (
                        service.users()
                        .messages()
                        .get(
                            userId="me",
                            id=message["id"],
                            format="full",
                            metadataHeaders=None,
                        )
                        .execute()
                    )

                    subject = ""
                    for header in msg["payload"]["headers"]:
                        if header["name"] == "Subject":
                            subject = header["value"]
                            break

                    sender = ""
                    for header in msg["payload"]["headers"]:
                        if header["name"] == "From":
                            sender = re.findall(
                                r"\b[\w\.-]+@[\w\.-]+\.\w+\b", header["value"]
                            )[0]
                            break
                    body = ""
                    if "parts" in msg["payload"]:
                        for part in msg["payload"]["parts"]:
                            if part["mimeType"] == "text/plain":
                                data = part["body"]["data"]
                                body = base64.urlsafe_b64decode(data).decode("utf-8")
                                break

                    email_info = {
                        "sender": sender,
                        "time": datetime.fromtimestamp(
                            int(msg["internalDate"]) / 1000
                        ).strftime("%Y-%m-%d %H:%M:%S"),
                        "subject": subject,
                        "body": body,
                    }
                    email_data.append(email_info)
                pbar.close()
            email_data = sort_by_time(email_data)[0:number]
            return {"results": email_data}
        except Exception as e:
            print(e)
            return None

    def _send(self, mail_dict: dict):
        recipient_mail = mail_dict["recipient_mail"]
        subject = mail_dict["subject"]
        body = mail_dict["body"]
        credential = self.credential
        service = build("gmail", "v1", credentials=credential)

        message = MIMEMultipart()
        message["to"] = recipient_mail
        message["subject"] = subject

        message.attach(MIMEText(body, "plain"))

        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode("utf-8")
        try:
            message = (
                service.users()
                .messages()
                .send(userId="me", body={"raw": raw_message})
                .execute()
            )
            return {"state": True}
        except HttpError as error:
            print(error)
            return {"state": False}

    def convert_action_to(self, action_name: str):
        assert (
            action_name.lower() in self.__VALID_ACTION__
        ), f"Action `{action_name}` is not allowed! The valid action is in `{self.__VALID_ACTION__}`"
        self.action = action_name.lower()

    def func(self, mail_dict: dict):
        if "action" in mail_dict:
            assert mail_dict["action"].lower() in self.__VALID_ACTION__
            self.action = mail_dict["action"]
        functions = {"read": self._read, "send": self._send}
        return functions[self.action](mail_dict)
