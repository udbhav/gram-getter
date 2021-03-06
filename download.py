import argparse, os, pprint, datetime
import dateutil.parser
import requests
from jinja2 import Template

parser = argparse.ArgumentParser(description='Download instagrams with a certain tag.')
parser.add_argument('--limit', help='Amount to download', type=int)
parser.add_argument('--client_id', help='Instagram Client ID')
parser.add_argument('--tag', help='Instagram Tag')
parser.add_argument('--date', help='Date')
args = parser.parse_args()

url = "https://api.instagram.com/v1/tags/%s/media/recent?client_id=%s" % (args.tag, args.client_id)
grabbed_data = []
keep_going = True

if args.date:
    date = dateutil.parser.parse(args.date).date()
else:
    date = None

pp = pprint.PrettyPrinter(indent=4)

while keep_going:
    resp = requests.get(url).json()
    photos = resp['data']
    for p in photos:
        photo = {'url': p['link'], 'image': p['images']['standard_resolution']['url']}
        if date:
            created = datetime.date.fromtimestamp(float(p['created_time']))
            if created >= date:
                grabbed_data.append(photo)
            else:
                keep_going = False
        else:
            grabbed_data.append(photo)

    next_url = resp['pagination'].get("next_url", None)
    if next_url and len(grabbed_data) < args.limit:
        url = next_url
    else:
        keep_going = False

print(len(grabbed_data))

def download_file(url):
    local_filename = url.split('/')[-1]
    r = requests.get(url)
    with open("download/%s" % local_filename, 'wb') as f:
        for chunk in r.iter_content(chunk_size=1024): 
            if chunk: # filter out keep-alive new chunks
                f.write(chunk)
    return

# if not os.path.exists("download"):
#     os.makedirs("download")

# for item in grabbed_data:
#     download_file(item['image'])

with open("index.html", "r") as f:
    template = Template(f.read())
    output = template.render(photos=grabbed_data)
    with open("output.html", "w") as wf:
        wf.write(output)
