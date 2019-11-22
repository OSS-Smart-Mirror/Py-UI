import os
import slack

slack_token = os.environ["SLACK_API_KEY"]
client = slack.WebClient(token=slack_token)

def send_message(message="", channel="alerts"):
    client.chat_postMessage(
      channel=channel,
      text=message
    )

def send_image(filepath="", channel="alerts"):
    client.files_upload(
      channels=channel,
      file=filepath,
      title="Test upload"
    )

if __name__ == "__main__":
    send_message(message="testing", channel="random")
