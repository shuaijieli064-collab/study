"""
启动智校通服务并生成公网访问链接
"""
import os
import sys
import time
import socket
from threading import Thread
from pyngrok import ngrok

def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
    finally:
        s.close()
    return ip

def start_server():
    os.system(f'python "{os.path.join(os.path.dirname(__file__), "app.py")}"')

def main():
    print("=" * 50)
    print("智校通 - 分享链接生成器")
    print("=" * 50)

    local_ip = get_local_ip()
    print(f"\n本机地址: http://{local_ip}:5000")

    ngrok_tunnel = ngrok.connect(5000)
    public_url = ngrok_tunnel.public_url
    print(f"\n公网地址: {public_url}")
    print("\n分享这个链接给别人，他们就可以直接访问你的智校通！")

    print("\n按 Ctrl+C 停止服务")
    print("=" * 50)

    try:
        server_thread = Thread(target=start_server, daemon=True)
        server_thread.start()

        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n正在关闭...")
        ngrok.kill()

if __name__ == "__main__":
    main()