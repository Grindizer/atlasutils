
import re
import json
import sys

def log_push(result, log):
    iter = 0
    last_message = ""
    for message in result:
        message = json.loads(message)
        if "error" in message:
            log(message["error"], fg='red')
            sys.exit(1)
        else:
            # can take a moment, so distract the dev ...
            w = ['|', '/', '-', '\\'][iter % 4]
            log("\rIn progress: {0}".format(w), nl=False, fg='green')
            iter += 1
            last_message = message
    log('\rPush done.         \n', fg='green')
    return last_message

def log_build(result, log):
    last_message = ""
    for message in result:
        if 'stream' in message:
            log(message['stream'][:-1])
            last_message = message['stream'][:-1]
        if 'error' in message:
            log(message['error'])

    srch = r'Successfully built ([0-9a-f]+)'
    match = re.search(srch, last_message)
    image_id = None
    if match:
        image_id = match.group(1)
    return image_id