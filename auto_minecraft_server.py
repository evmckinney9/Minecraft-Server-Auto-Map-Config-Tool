#get minecraft map and save
import requests, zipfile, io, os, shutil, subprocess

path = 'c:/users/evmck_jo2z2u/downloads/minecraft_maps/server_map/'

try:
    shutil.rmtree(path)
except:
    pass

headers = {}
url = input("Map url: ")
headers['Referer'] = url
r = requests.get(url)
if not r.ok:
    print("bad url")
    exit()
text = r.text
index = text.find("MC Version:")
version = text[index+58:index+66]
version = ''.join(x for x in version if x.isdigit() or x=='.')
print("detected mc version " + version)


#saving
print("downloading...")
try:
    r = requests.get(url+"/download", headers=headers, allow_redirects=True)
    z = zipfile.ZipFile(io.BytesIO(r.content))
    z.extractall(path)

except:
    print("download failed")
    exit()

#format files for server
zip_name = os.listdir(path)[0]
os.rename(path + zip_name,path+'world')
path = path+'world'

server_return = os.popen("ssh minecraftuser@192.168.1.249 'bash -s' < validate_jar.sh").read()
minecraft_jar = "minecraft_server-" + version + ".jar"
if not minecraft_jar in server_return:
    print("fetching new server jar file")
    r = requests.get("https://mcversions.net/")
    jar_url = "-1"
    for line in r.text.split('\n'):
        if minecraft_jar in line:
            jar_url = line[9:line.find(".jar")+4]
    if jar_url == "-1":
        print("failed to retrieve server jar")
        exit()
    p= subprocess.Popen("ssh minecraftuser@192.168.1.249 'bash -s' < download_jar.sh " + minecraft_jar + " " + jar_url, stdout=subprocess.PIPE, shell=True)
    p.wait()
    print("download jar complete")

#stop server, delete usercache and world file
print("cleaning server of old world")
p = subprocess.Popen("ssh minecraftuser@192.168.1.249 'bash -s' < server_stop.sh", stdout=subprocess.PIPE, shell=True)
p.wait()
print("clean server complete")

#transfer files
print("transferring world files")
p = subprocess.Popen("scp -r " + path + " minecraftuser@192.168.1.249:/home/minecraftuser/minecraftdir", stdout=subprocess.PIPE, shell=True)
p.wait()
print("file transfer complete")

#start server
print("restarting server with new world")
p= subprocess.Popen("ssh minecraftuser@192.168.1.249 'bash -s' < server_start.sh " + minecraft_jar, stdout=subprocess.PIPE, shell=True)
p.wait()
print("restart complete")
