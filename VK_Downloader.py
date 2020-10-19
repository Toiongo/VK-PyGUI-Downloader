import PySimpleGUI as SGUI
from mutagen.mp3 import MP3
import vk_api
from vk_api import audio
import requests
import os

REQUEST_STATUS_CODE = 200
name_dir = '_music_vk'
path = r'./audio' + name_dir
login = ''
password = ''
my_id = ''

if not os.path.exists(path):
    os.makedirs(path)

layout = [
    [SGUI.Text("Login: "), SGUI.InputText(pad=(31, 0, 0, 0), key='login')],
    [SGUI.Text("Password: "), SGUI.InputText(password_char="*", key='password')],
    [SGUI.Text("VK ID: "), SGUI.InputText(pad=(28, 0, 0, 0), key='id')],
    [SGUI.Listbox(values=(), size=(60, 20), key='tracks')],
    [SGUI.Text("№ Of tracks: "), SGUI.InputText(key='num_of_tracks', size=(10, 10), default_text="5")],
    [SGUI.InputText(key='error_field', readonly=True, size=(62, 10))],
    [SGUI.Button("Get tracks"), SGUI.Button("Download"), SGUI.Button("Cancel")]
]

window = SGUI.Window('VK Downloader', layout)

bitlist = []
urllist = []

while True:
    event, values = window.read()
    if event in (SGUI.WIN_CLOSED, 'Cancel'):
        break
    if event == "Get tracks":
        if not values['login'] or not values['password'] or not values['id']:
            window.Element('error_field').Update(value='Please enter login, password and id.')
            continue
        else:
            if values['num_of_tracks']:
                try:
                    counter = int(values['num_of_tracks'])
                except Exception as e:
                    window.Element('error_field').Update(value=e)
                    continue

            try:
                login = values['login']
                password = values['password']
                my_id = values['id']

                vk_session = vk_api.VkApi(login=login, password=password)
                vk_session.auth()
                vk = vk_session.get_api()
                vk_audio = audio.VkAudio(vk_session)

                os.chdir(path)
            except Exception as e:
                window.Element('error_field').Update(value=e)
                continue

            bitrates = []

            for i in vk_audio.get(owner_id=my_id):
                try:
                    urllist.append(i)
                    r = requests.get(i['url'])
                    if r.status_code == REQUEST_STATUS_CODE:
                        with open(''.join(e for e in (i["artist"] + ' - ' + i["title"] + '.mp3') if e.isalnum() or e in " .-_"), 'wb') as output_file:
                            print("Downloading temp file: " + i['title'] + '.mp3')
                            output_file.write(r.content)
                        try:
                            print("Finding out bitrate of: " + i['title'] + '.mp3')
                            f = MP3(output_file.name)
                            bitrates.append(
                                [i["artist"] + ' - ' + i["title"] + '.mp3', "{0:.00f}".format(f.info.bitrate / 1000), i['url']])
                        finally:
                            print("Removing temp file: " + i['title'] + '.mp3' + "\n")
                            os.remove(output_file.name)
                            counter -= 1
                            if (counter <= 0): break
                except OSError as e:
                    print(e)
                    window.Element('error_field').Update(value=e)

            index_counter = 1

            for v in bitrates:
                bitlist.append(str(index_counter) + '. ' + v[0] + ' /:/ Bitrate: ' + v[1] + "kbps")
                index_counter += 1

            window.Element('tracks').Update(values=bitlist)
    if event == 'Download':
        try:
            i = urllist[int(values['tracks'][0][0]) - 1]
            r = requests.get(i['url'])
            if r.status_code == REQUEST_STATUS_CODE:
                with open(''.join(e for e in (i["artist"] + ' - ' + i["title"] + '.mp3') if e.isalnum() or e in " .-_"), 'wb') as output_file:
                    print("Downloading file: " + i["artist"] + ' - ' + i["title"] + '.mp3')
                    output_file.write(r.content)
        except OSError as e:
            print(e)
            window.Element('error_field').Update(value='Please select a track.')


window.close()