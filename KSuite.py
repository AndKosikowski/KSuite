import tkinter
from tkinter import filedialog
import os 
import re
import shutil
import pathlib
import subprocess
import sys

tkinter.Tk().withdraw() # prevents an empty tkinter window from appearing

this_folder_path = ""

def install_plugins(keepass_path):

    if not os.path.isdir(keepass_path):
        tkinter.messagebox.showerror("KeePass not in default installation location","KeePass not in default installation location")
        return

    plugins_to_install_path = os.path.join(this_folder_path,"Plugins")
    plugins_destination_path = os.path.join(keepass_path,"Plugins")
    
    shutil.rmtree(plugins_destination_path,ignore_errors=True) #scary
    shutil.copytree(plugins_to_install_path, plugins_destination_path,dirs_exist_ok=True)

def copy_databases(keepass_data):
    database_path = os.path.join(this_folder_path,"Install","Database.kdbx")
    database_key_path = os.path.join(this_folder_path, "Install", "DataBase.keyx")
    shutil.copy(database_path,keepass_data)
    shutil.copy(database_key_path,keepass_data)

def copy_ssh_key(ssh_folder_path,key):
    ssh_id_path = os.path.join(ssh_folder_path,key)

    if os.path.exists(ssh_id_path):
        tkinter.messagebox.showerror(f"{key} already exists, talk to Andrew if unsure",f"{key} already exists, talk to Andrew if unsure")
        return
    

    id_path = os.path.join(this_folder_path,"Install",key)
    id_pub_path = os.path.join(this_folder_path,"Install",key+".pub")

    if os.path.exists(id_path):    
        shutil.copy(id_path,ssh_folder_path)
    
    if os.path.exists(id_pub_path):
        shutil.copy(id_pub_path,ssh_folder_path)



def copy_ssh_keys():

    home_dir = os.path.expanduser('~')

    ssh_folder_path = os.path.join(home_dir,".ssh")

    pathlib.Path(ssh_folder_path).mkdir(parents=True, exist_ok=True)  #make dirs if they dont exist

    copy_ssh_key(ssh_folder_path=ssh_folder_path,key="id_rsa")
    copy_ssh_key(ssh_folder_path=ssh_folder_path,key="id_ed25519")

    
    


def add_triggers(config_path,keepass_path):

    if not os.path.isfile(config_path):
        tkinter.messagebox.showerror("Config file not in AppData/Roaming in default installation location","Config file not in AppData/Roaming in default installation location")
        return
    
    home_dir = os.path.expanduser('~')

    database_path = os.path.join(home_dir,"Documents", "KeePass","Database.kdbx")

    enforced_path = os.path.join(keepass_path, "KeePass.config.enforced.xml")

    username_file = os.path.join(this_folder_path,"Install","Username.txt")

    with open(username_file,"r") as f:
        username = f.read().lower().strip()

    # database_path = filedialog.askopenfilename(title="Select your database file (.dbkx file)") # Can be used to select yourself

    # username = tkinter.simpledialog.askstring("Input your username","Input your username").lower() # Can be used to select yourself


    with open(config_path, "r") as f:
        file_contents = f.read()

    with open(enforced_path, "r") as f:
        enforced_file_contents = f.read()

    trigger_text = '''         <TriggerSystem>
                    <Triggers>
                        <Trigger>
                            <Guid>fzsup1PJykquTCZ1hcH5GQ==</Guid>
                            <Name>Sync after save or load</Name>
                            <Events>
                                <Event>
                                    <TypeGuid>s6j9/ngTSmqcXdW6hDqbjg==</TypeGuid>
                                        <Parameters>
                                        <Parameter>0</Parameter>
                                        <Parameter>{0}</Parameter>
                                    </Parameters>
                                </Event>
                                <Event>
                                    <TypeGuid>5f8TBoW4QYm5BvaeKztApw==</TypeGuid>
                                    <Parameters>
                                        <Parameter>0</Parameter>
                                        <Parameter>{0}</Parameter>
                                    </Parameters>
                                </Event>
                            </Events>
                            <Conditions />
                            <Actions>
                                <Action>
                                    <TypeGuid>tkamn96US7mbrjykfswQ6g==</TypeGuid>
                                    <Parameters>
                                        <Parameter />
                                        <Parameter>0</Parameter>
                                    </Parameters>
                                </Action>
                                <Action>
                                <TypeGuid>Iq135Bd4Tu2ZtFcdArOtTQ==</TypeGuid>
                                    <Parameters>
                                        <Parameter>sftp://andrewkosikowski.com:22/R:/Databases/{2}/Database.kdbx</Parameter>
                                        <Parameter>{1}</Parameter>
                                        <Parameter />
                                    </Parameters>
                                </Action>
                                <Action>
                                    <TypeGuid>tkamn96US7mbrjykfswQ6g==</TypeGuid>
                                    <Parameters>
                                        <Parameter />
                                        <Parameter>1</Parameter>
                                    </Parameters>
                                </Action>
                            </Actions>
                        </Trigger>
                    </Triggers>
                </TriggerSystem>'''


    file_contents =  re.sub('(<TriggerSystem>)(.|\n)*<\/TriggerSystem>',trigger_text,file_contents)
    database_path = database_path.replace("/","\\") 
    file_contents = file_contents.format(database_path,username,username.capitalize()) #Have to format it after as database_path.replace and regex/re don't play nice

    enforced_file_contents = re.sub('(<TriggerSystem>)(.|\n)*<\/TriggerSystem>',trigger_text,enforced_file_contents)
    enforced_file_contents = enforced_file_contents.format(database_path,username,username.capitalize())

    with open(config_path, "w") as f:
        f.write(file_contents)

    with open(enforced_path, "w") as f:
        f.write(enforced_file_contents)


def set_recent_database(config_path):
    with open(config_path, "r") as f:
        file_contents = f.read()
    home_dir = os.path.expanduser('~')

    database_path = os.path.join(home_dir,"Documents", "KeePass","Database.kdbx")
    database_key_path = os.path.join(home_dir,"Documents", "KeePass","Database.keyx")

    last_used_file_text = '''<LastUsedFile>
			<Path>{0}</Path> 
			<CredProtMode>Obf</CredProtMode>
			<CredSaveMode>NoSave</CredSaveMode>
		</LastUsedFile>'''
    
    file_contents =  re.sub('(<LastUsedFile>)(.|\n)*<\/LastUsedFile>',last_used_file_text,file_contents)
    database_path = database_path.replace("/","\\") 
    file_contents = file_contents.format(database_path) #Have to format it after as database_path.replace and regex/re don't play nice

    last_used_key_file_text = '''<KeySources>
        <Association>
            <DatabasePath>{0}</DatabasePath>
		    <KeyFilePath>{1}</KeyFilePath> 
        </Association>
	</KeySources>'''


    if "<KeySources />" in file_contents or "<KeySources />" in file_contents:
        file_contents = re.sub('(<KeySources />)|(<KeySources/>)',last_used_key_file_text,file_contents)
    else:
        file_contents = re.sub('(<KeySources>)(.|\n)*<\/KeySources>',last_used_key_file_text,file_contents)

    database_key_path = database_key_path.replace("/","\\")
    file_contents = file_contents.format(database_path,database_key_path)

    with open(config_path, "w") as f:
        f.write(file_contents)
    


def copy_base_config(config_path, keepass_path):

    install_path = os.path.join(this_folder_path,"Install")

    enforced_path = os.path.join(keepass_path,"KeePass.config.enforced.xml")

    install_config_path = os.path.join(install_path,"KeePass.config.xml")
    install_enforced_path = os.path.join(install_path,"KeePass.config.enforced.xml")

    shutil.copy(install_config_path,config_path)
    shutil.copy(install_enforced_path,enforced_path)

    




if __name__ == "__main__":


    if getattr(sys, 'frozen', False):
        # If the application is run as a bundle, the PyInstaller bootloader
        # extends the sys module by a flag frozen=True and sets the app 
        # path into variable _MEIPASS'.
        this_folder_path = os.path.dirname(sys.executable)
    else:
        this_folder_path = os.path.dirname(os.path.abspath(__file__))

    install_path = os.path.join(this_folder_path,"Install")

    home_dir = os.path.expanduser('~')

    config_path = os.path.join(home_dir, "AppData", "Roaming", "KeePass","KeePass.config.xml")

    keepass_data = os.path.join(home_dir,"Documents", "KeePass")

    keepass_path = """C:\Program Files\KeePass Password Safe 2"""

    
    pathlib.Path(keepass_data).mkdir(parents=True, exist_ok=True)  #make dirs if they dont exist
    pathlib.Path(os.path.dirname(config_path)).mkdir(parents=True, exist_ok=True)  #make dirs if they dont exist
    pathlib.Path(keepass_path).mkdir(parents=True, exist_ok=True)  #make dirs if they dont exist

    copy_base_config(config_path=config_path, keepass_path=keepass_path)

    copy_databases(keepass_data=keepass_data)

    

    add_triggers(config_path=config_path,keepass_path=keepass_path)

    set_recent_database(config_path=config_path)

    copy_ssh_keys()

    for file in os.listdir(install_path):
        if "KeePass" in file and "Setup.exe" in file:
            cmd = os.path.join(install_path, file)
            subprocess.call(cmd, shell=True)

    

    install_plugins(keepass_path=keepass_path)


    for file in os.listdir(install_path):
        if "RaiDriveSetup.exe" in file:
            cmd = os.path.join(install_path, file)
            subprocess.call(cmd, shell=True)


