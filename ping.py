import struct
import array
import socket
import argparse
import time

def send_icmp(s:socket,address:tuple,icmp_data:bytes):
    s.settimeout(20)
    s.sendto(icmp_data,address)
    data=s.recvfrom(1024)[0]
    icmp_resp=data[20:28]
    sss=struct.unpack("!BBHHHBBHII",data[0:20])
    return sss

def check_num(data:bytearray):
    a=array.array("b",data)
    length=len(a)
    sum=0
    for i in range(0,length,2):
        if i+1<length:
            high=a[i]<<8
            low=a[i+1]
            sum=sum+high+low
    if i+1==length:
        sum+=a[i]
    high=(sum>>16)&0xffff
    while high!=0:
        sum=high+sum&0xffff
        high=(sum>>16)&0xffff
    return (~sum)&0xffff

def create_icmp(length):
    icmp_header=[8,0,0,1,1] # 长度分别为1 1 2 2 2
    bin_data=struct.pack(">bbHHH",*icmp_header)
    new_bin_data=bin_data+b"\x00"*length
    res=check_num(new_bin_data)
    icmp_header=(8,0,res,1,1)
    bin_data=struct.pack(">bbHHH",*icmp_header)
    new_bin_data=bin_data+b"\x00"*length
    return new_bin_data

def cmd_parse():
    args=argparse.ArgumentParser()
    args.add_argument("-u","--url",help="目标地址",type=str)
    args.add_argument("-c","--count",help="发包数量",type=int,default=4)
    args.add_argument("-l","--length",help="数据包长度",type=int,default=32)
    args.parse_args()
    return args.parse_args()

if __name__=="__main__":
    args=cmd_parse()
    url=args.url
    count=args.count
    length=args.length
    s=socket.socket(socket.AF_INET,socket.SOCK_RAW,socket.getprotobyname("icmp"))
    address=socket.getaddrinfo(url,0)[0][4]
    print(f"正在 Ping {url} [{address[0]}] 具有 {length} 字节的数据:")
    for _ in range(count):
        time.sleep(1)
        icmp_data=create_icmp(length=length)
        res=send_icmp(s=s,address=address,icmp_data=icmp_data)
        print(f"来自 {address[0]} 的回复: 字节={length} 时间=14ms TTL={res[5]}")

