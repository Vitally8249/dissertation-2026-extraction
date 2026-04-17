def check_device():
try:
lockdown = create_using_usbmux(autopair=False)
except:
lockdown = None
return(lockdown)
def pair_device(paired):
global lockdown
lockdown_unpaired = lockdown
try:
lockdown = create_using_usbmux()
global ispaired
ispaired = True
paired.set(True)
except:
lockdown = lockdown_unpaired
paired.set(False)
return(lockdown)
lockdown = check_device()
try:
language = lockdown.language
ispaired = True
log(f"Paired with device: {udid}")
except:
ispaired = False

# Device Info
dev_name = lockdown.display_name
hardware = lockdown.hardware_model
product = lockdown.product_type
udid = lockdown.udid
ecid = str(lockdown.ecid)
dversion = lockdown.product_version
w_mac = lockdown.wifi_mac_address
name = lockdown.get_value("","DeviceName")
build = lockdown.get_value("","BuildVersion")

# Extended Info
imei = lockdown.get_value("","InternationalMobileEquipmentIdentity")
imei2 = lockdown.get_value("","InternationalMobileEquipmentIdentity2")
snr = lockdown.get_value("","SerialNumber")
mlbsnr = lockdown.get_value("","MLBSerialNumber")
d_tz = lockdown.get_value("","TimeZone")
b_mac = lockdown.get_value("","BluetoothAddress")
mnr = lockdown.get_value("", "ModelNumber")
hardware_mnr = f"{hardware}, {mnr}"
disk1 = lockdown.get_value("com.apple.disk_usage","TotalDiskCapacity")
free1 = lockdown.get_value("com.apple.disk_usage","AmountDataAvailable")
language = lockdown.language

# Installed Applications
from pymobiledevice3.services import installation_proxy
# Get Apps installed by the User
apps = \
installation_proxy.InstallationProxyService(lockdown).get_apps("User")
all_apps = \
installation_proxy.InstallationProxyService(lockdown).get_apps()
app_id_list = []
# order the apps alphabetically
sorted_apps =
sorted(apps.keys(),key=lambda app:
apps.get(app).get('CFBundleDisplayName', '').lower()) #Continuation
for app in sorted_apps:
app_id_list.append(app)

# App Documents Directory
doc_list = []
for app in sorted_apps:
try:
apps.get(app)['UIFileSharingEnabled']
doc_list.append("yes")
except:
doc_list.append("no")

# Hidden Apps
if int(dversion.split(".")[0]) >= 14:
springboard = \
SpringBoardServicesService(lockdown).get_icon_state()
else:
springboard = None
try: al = str(len(max(app_id_list, key=len)))
except: al = 40
for app in app_id_list:
app_name = apps.get(app)['CFBundleDisplayName']
if len(app_name) > 20:
app_name = f'{app_name[:17]}...'
try:
apps.get(app)['UIFileSharingEnabled']
sharing = 'yes'
except:
sharing = 'no'
if springboard != None:
if app in str(springboard):
state = "visible"
else:
state = "absent"
file.write("\n" + '{:{l}}'.format(app_name, l=20) + "\t" + '{:
{l}}'.format(app, l=al) + "\t [" + sharing + "]") #Continuation
if springboard != None:
file.write("\t\t" + state)

# Encrypted Backup
from pymobiledevice3.services.mobilebackup2 import
Mobilebackup2Service
Mobilebackup2Service(lockdown).change_password(new="12345")

# AFC Media Directory
from pymobiledevice3.services.afc import AfcService, LockdownService
dest = "Media"
os.mkdir(dest)
for line in AfcService(lockdown).dirlist("/"):
media_list.add(line)
media_count = len(media_list)
# Remove "DCIM" from list when calling AFC in adv. logical flow
if l_type != "folder":
media_list.remove("DCIM")
for entry in media_list:
pull(self=AfcService(lockdown),relative_src=entry, dst=dest)

# App Data
from pymobiledevice3.services.house_arrest import HouseArrestService
for app in app_id_list:
if doc_list[i] == 'yes':
file_path = os.path.join(".tar_tmp/app_doc/", app,
str((apps.get(app)['EnvironmentVariables'])
['CFFIXED_USER_HOME'])[1:], "Documents/") #Continuation
os.makedirs(file_path, exist_ok=True)
pull(self=HouseArrestService(lockdown, bundle_id=app,
documents_only=True), relative_src="/Documents/.",
dst=file_path)
app_dest = os.path.join(str((apps.get(app)['EnvironmentVariables'])
['CFFIXED_USER_HOME'])[1:], "Documents/") #Continuation
for root, dirs, files in os.walk(file_path):
for file in files:
source_file = os.path.join(root, file)
filename = os.path.relpath(source_file, file_path)
app_arc = posixpath.join(app_dest, filename)
if app_arc not in unback_set and
os.path.isfile(file_path): #Continuation
tar.add(file_path, app_arc, recursive=False)
else:
pass

# Crash Logs
from pymobiledevice3.services.crash_reports import
CrashReportsManager
crash_list = []
try:
for entry in CrashReportsManager(lockdown).ls(""):
crash_list.append(entry)
try: os.mkdir(crash_dir)
except: pass
for entry in crash_list:
pull(self=AfcService(lockdown,
service_name="com.apple.crashreportcopymobile"),
relative_src=entry, dst=crash_dir)


# Unified logs 
from pymobiledevice3.services.os_trace import OsTraceService
def collect_ul(self, time, text, waitul):
try: os.mkdir("unified_logs")
except: pass
uname = f'{udid}_{datetime.now().strftime
("%Y_%m_%d_%H_%M_%S")}.logarchive' #Continuation
try:
OsTraceService(lockdown).collect(out= \
os.path.join("unified_logs", uname), start_time=time)
text.configure(text=f"Unified Logs written to:\n{uname}")
log(f"Collected Unified Logs as {uname}")
waitul.set(1)
except:
text.configure(text="Error: \nCoud not collect logs - \
Maybe the device or its iOS version is too old.")
log("Error collecting Unified Logs")
waitul.set(1)
try: os.rmdir("unified_logs")
except: pass

# Sysdiagnose
from pymobiledevice3.services.crash_reports import
CrashReportsManager
self.diagsrv = CrashReportsManager(lockdown)
try:
sysdiagname = self.diagsrv._get_new_sysdiagnose_filename()
text.configure(text="Creation of Sysdiagnose archive has been
started.")
#Continuation
self.diagsrv._wait_for_sysdiagnose_to_finish()
text.configure(text="Pulling the Sysdiagnose archive from the
device") #Continuation
self.diagsrv.pull(out=f"{udid}_sysdiagnose.tar.gz",
entry=sysdiagname,erase=True) #Continuation
text.configure(text="Extraction of Sysdiagnose archive
completed!") #Continuation
log("Extracted Sysdiagnose file")
except:
text.configure(text="Extraction of Sysdiagnose canceled!")
log("Sysdiagnose extraction canceled")

# iTunes Backup Decrpytion
from iOSbackup import iOSbackup
import pandas as pd
def init_backup_decrypt(self, change):
global b
global backupfiles
b = iOSbackup(udid=udid, cleartextpassword="12345",
derivedkey=None, backuproot="./") #Continuation
#Load Backup with Password
key = b.getDecryptionKey() #Get decryption Key
b = iOSbackup(udid=udid, derivedkey=key, backuproot="./")
#Load Backup again with Key
backupfiles = pd.DataFrame(b.getBackupFilesList(), \
columns=['backupFile','domain','name','relativePath'])

unbackup_path = {
"KeychainDomain": "/var/Keychain",
"CameraRollDomain": "/var/mobile",
"MobileDeviceDomain": "/var/MobileDevice",
"WirelessDomain": "/var/wireless",
"InstallDomain": "/var/installd",
"KeyboardDomain": "/var/mobile",
"HomeDomain": "/var/mobile",
"SystemPreferencesDomain": "/var/preferences",
"DatabaseDomain": "/var/db",
"TonesDomain": "/var/mobile",
"RootDomain": "/var/root",
"BooksDomain": "/var/mobile/Media/Books",
"ManagedPreferencesDomain": "/var/Managed Preferences",
"HomeKitDomain": "/var/mobile",
"MediaDomain": "/var/mobile",
"HealthDomain": "/var/mobile/Library",
"ProtectedDomain": "/var/protected",
"NetworkDomain": "/var/networkd/",
"AppDomain": "/var/mobile/Containers/Data/Application",
"AppDomainGroup": "/var/mobile/Containers/Shared/AppGroup",
"AppDomainPlugin": "/var/mobile/Containers/Data/PluginKitPlugin",
"SysContainerDomain": "/var/containers/Data/System",
"SysSharedContainerDomain": "/var/containers/Shared/SystemGroup"
}

# Installed Apps
for file in line_list:
unback_set = set()
m_unback_set = set()
b.getFileDecryptedCopy(relativePath=file,
targetName=fileout, targetFolder=os.path.join(".tar_tmp",
"itunes_bu")) #Continuation
filedomain = backupfiles.loc[backupfiles['relativePath'] ==
file, 'domain'].iloc[0]
file_path = os.path.join('.tar_tmp', 'itunes_bu', fileout)
if "AppDomain-" in filedomain:
appfile = filedomain.split("-", 1)[1]
all_apps.get(appfile)['Container']
elif "AppDomainGroup-" in filedomain:
appfile = filedomain.split("-")[1]
for app in all_apps:
if all_apps[app]['GroupContainers'].get(appfile)
is not None:
tarpath = all_apps[app][
'GroupContainers'].get(appfile)
break
else:
tarpath = f"/private{unback_path[
'AppDomainGroup']}/{appfile}"

# iTunes Metadata
if l_type == "PRFS":
appfile = installation_proxy.InstallationProxyService(
lockdown).browse(attributes=['CFBundleIdentifier',
'iTunesMetadata', 'Path') #Continuation
for app in appfile:
try:
if "Bundle" in app['Path']:
bpath = app['Path']
bundlepath = f'{bpath.strip("/")}/'
bundle_folder = tarfile.TarInfo( \
name=bundlepath)
bundle_folder.type = tarfile.DIRTYPE
tar.addfile(bundle_folder)
try:
itunesplist = app['iTunesMetadata']
itunes_path = "/".join(list(bpath.
split('/')[0:-1]))
metafile = os.path.join(".tar_tmp",\
"iTunesMetadata.plist")
with open(metafile, "wb") as file:
file.write(itunesplist)
tar.add(metafile, arcname=(f"{ \
itunes_path}/iTunesMetadata.plist"))
os.remove(metafile)
except:
pass
except:
pass