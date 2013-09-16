import json
import os
import sys

import soundcloud

CLIENT_ID     = 'ffc80dc8b5bd435a15f9808724f73c40'
CLIENT_SECRET = 'b299b6681e00dfd9f5015639c7f5fe29'
SC_CONF       = os.path.expanduser('~/.sc')


def get_access_token(username, password):
    client = soundcloud.Client(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        username=username,
        password=password,
    )

    return client.access_token


def get_client():
    if not os.path.exists(SC_CONF):
        print 'Run auth command to authenticate and save access token.'
        sys.exit(1)

    with open(SC_CONF) as f:
        access_token = json.load(f)['access_token']

    client = soundcloud.Client(access_token=access_token)
    return client


def compress_track(filename=None, bitrate=320, title='', artist='', album='', year=''):
    if not filename:
        raise Exception('Filename required argument')

    os.system('lame -b %d --tt "%s" --ta "%s" --tl "%s" --ty %s %s' % (bitrate, title, artist, album, year, filename))


def upload_track(filename=None, title=None, private=True):
    filename = os.path.expanduser(filename)

    if not filename:
        raise Exception('Filename required argument')

    client = get_client()

    if not title:
        title = os.path.splitext(os.path.basename(filename))[0]

    track = {
        'title': title,
        'asset_data': open(filename, 'rb')
    }

    if private:
        track['sharing'] = 'private'

    print track
    track = client.post('/tracks', track=track)

    return track


def command_upload(args):
    if args.compress:
        compress_track(
            filename=args.filename,
            bitrate=args.bitrate,
            title=args.title,
            artist=args.artist,
            album=args.album,
            year=args.year
        )
        args.filename.replace('.wav', '.mp3')

    upload_track(
        filename=args.filename,
        title=args.title,
        private=args.private
    )


def command_auth(args):
    import getpass

    _username = getpass.getuser()
    username = raw_input('Enter username (%s): ' % _username)
    if not username:
        username = _username

    password = getpass.getpass('Enter password: ')

    with open(SC_CONF, 'w') as f:
        json.dump({'access_token': get_access_token(username, password)}, f)

    print 'Saved access_token.'

def main():
    import argparse
    from datetime import date

    args = sys.argv

    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()

    upload_parser = subparsers.add_parser('upload', help='Upload track to soundcloud')
    upload_parser.add_argument('filename', action='store', help='File to upload')
    upload_parser.add_argument('--private', action='store_true', help='Make track private')
    upload_parser.add_argument('--compress', action='store_true', help='Compress file')
    upload_parser.add_argument('--bitrate', default=320, help='Compress file')
    upload_parser.add_argument('--tags', help='Tags for track')
    upload_parser.add_argument('--title', help='id3 title')
    upload_parser.add_argument('--album', help='id3 album')
    upload_parser.add_argument('--year', default=date.today().year, help='id3 year')
    upload_parser.set_defaults(command=command_upload)

    auth_parser = subparsers.add_parser('auth', help='Authenticate and save access token')
    auth_parser.set_defaults(command=command_auth)

    args = parser.parse_args()
    args.command(args)

if __name__ == '__main__':
    main()
