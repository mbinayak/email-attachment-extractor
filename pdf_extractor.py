from __future__ import print_function

import email
import os

bucket_id = 'navf971mgt9kmaa4m3evieocq8pm5i9tg3154r01'

def main():
    f = open(bucket_id, "rt")
    # msg = email.message_from_string(response.get()["Body"].read())
    msg = email.message_from_string(f.read())
    if len(msg.get_payload()) == 2:
        # The first attachment
        attachment = msg.get_payload()[1]

        # Extract the attachment into /tmp/output
        extract_attachment(attachment)

    else:
        print("Could not see file/attachment.")

def extract_attachment(attachment):
    try:
        path = 'attachments/{directory}'.format(directory = bucket_id)
        os.makedirs(path)
        print(attachment.get_content_type(), attachment.get_filename())
        if "pdf" in attachment.get_content_type():
            file_path = '{path}/{file_name}'.format(path = path, file_name = attachment.get_filename())
            open(file_path, 'wb').write(attachment.get_payload(decode=True))
    except Exception as e:
        print(e)
        raise e


if __name__== "__main__":
  main()


