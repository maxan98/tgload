# Делать сеё счастье многопоточным.
import os
import threading
import pickle
import argparse
import time
import pyrogram
from pyrogram import Client
from pyrogram.api import functions
from pyrogram.api.errors import FloodWait
from tqdm import tqdm
from tqdm import tgrange
def prgr(cur,total):
    print('Downloading',round(cur/2**20,3),'Of',round(total/2**20,3))
def savemedia(client,history):
    os.makedirs('media',exist_ok=True)
    os.makedirs('media/photos',exist_ok=True)
    os.makedirs('media/videos',exist_ok=True)
    os.makedirs('media/voice',exist_ok=True)
    os.makedirs('media/other',exist_ok=True)
    downloadedcounter = 0
    #mass = []
    #mass.append(tqdm(total=bbound-abound))

    for i in trange(len(history)):
        #mass[0].update(1)
        if type(history[i]) == pyrogram.api.types.MessageEmpty or type(history[i]) == pyrogram.api.types.MessageService:
            continue
        path = client.download_media(history[i],'media/',True)
        if path != None:
            downloadedcounter+=1
            #20. ---  100
            #2.  ---  x
            # 20x =200
            #print('Примерно скачали',round(100*downloadedcounter/bbound-abound,3),'%',bbound)
            if '.jpg' in path:
                name = os.path.basename(path)
                os.replace(path,'media/photos/'+name)
            elif '.oga' in path:
                name = os.path.basename(path)
                os.replace(path,'media/voice/'+name)
            elif '.mp4' in path:
                name = os.path.basename(path)
                os.replace(path,'media/videos/'+name)
            else:
                name = os.path.basename(path)
                os.replace(path,'media/other/'+name)
    #mass[0].close()
    print('THREAD FINISHED')
def gethistory(client,target):
    history = []  # List that will contain all the messages of the target chat      
    limit = 100  # Amount of messages to retrieve for each API call
    offset = 0  # Offset starts at 0
    print('Collecting messages..')
    while True:
        try:
            messages = client.send(
                functions.messages.GetHistory(
                    client.resolve_peer(target),
                    0, 0, offset, limit, 0, 0, 0
                )
            )
        except FloodWait as e:
            # For very large chats the method call can raise a FloodWait
            time.sleep(e.x)  # Sleep X seconds before continuing
            continue

        if not messages.messages:
            break  # No more messages left

        history.extend(messages.messages)
        offset += limit
        swr = 'Received '+str(offset+limit)+' messages'
        print(swr,end='\r')

        #sys.stdout.write('\r')

    return history

def main():
    parser = argparse.ArgumentParser(description = 'Telegram media parser')
    parser.add_argument('-d','--dump',help='Dumps dialog history for future use',action='store_true')
    parser.add_argument('-f','--file',help='Path to serialized dialogs')
    parser.add_argument('-n','--name',help='The name of the person whose dialogue you want to dump')
    #parser.add_argument('-t','--threads',help='Nuber of threads, using only on savemedia stage')
    ns = parser.parse_args()
    client = Client("tgload")
    client.start()
    target = ns.name  # "me" refers to your own chat (Saved Messages)
    if ns.dump:
        if ns.name == None:
            print('-n(ame) required')
            client.stop()
            exit()
        history = gethistory(client,ns.name)
        with open(ns.name+'.pkl', 'wb') as f:
            pickle.dump(history, f)
        client.stop()
        exit()

    elif ns.file != None:
        ns.name = ns.file
        history = []
        with open(ns.name+'.pkl', 'rb') as f:
            history = pickle.load(f)
        
        savemedia(client,history)
        client.stop()
        exit()
    else:
        if ns.name == None:
            print('-n(ame) required')
            client.stop()
            exit()
        history = gethistory(client,target)
        savemedia(client,history) 
        client.stop()
        exit()
    

    client.stop()



if __name__ == '__main__':
    main()
# Now the "history" list contains all the messages sorted by date in
# descending order (from the most recent to the oldest one)