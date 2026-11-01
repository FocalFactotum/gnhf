import os,pty,fcntl,termios,struct,subprocess,re,json,unicodedata
from pathlib import Path
out=Path('/home/captain/.no-mistakes/evidence/01M6C7SPVBG8B871T7KYJ30XGY')
out.mkdir(parents=True,exist_ok=True)
results=[]
for width,height in [(20,60),(5,100),(3,100),(2,100),(1,80),(1,8),(20,8),(63,60),(80,60)]:
    master,slave=pty.openpty()
    fcntl.ioctl(slave,termios.TIOCSWINSZ,struct.pack('HHHH',height,width,0,0))
    p=subprocess.Popen(['node','.live-renderer/drive.mjs'],stdin=slave,stdout=slave,stderr=slave)
    os.close(slave)
    data=b''
    while True:
        try:
            chunk=os.read(master,65536)
            if not chunk: break
            data+=chunk
        except OSError: break
    os.close(master)
    assert p.wait()==0
    text=data.decode()
    (out/f'terminal-{width}x{height}.ansi.txt').write_text(text)
    # First full frame is the actual initial terminal paint, preceding shutdown title restoration.
    frame=text.split('\x1b[H',1)[1]
    frame=re.sub(r'\x1b\][^\x07\x1b]*(?:\x07|\x1b\\)','',frame)
    frame=re.sub(r'\x1b\[[0-9;]*[A-Za-z]','',frame)
    lines=frame.replace('\r','').split('\n')
    cols=lambda s:sum(0 if unicodedata.combining(c) else 2 if unicodedata.east_asian_width(c) in ('W','F') else 1 for c in s)
    assert all(cols(line)<=width for line in lines),(width,max(map(cols,lines)))
    active='o' if width==1 else '🌑'
    assert active in frame,(width,height,frame)
    moonlines=[line for line in lines if '🌕' in line or '🌑' in line or (width==1 and line in ('O','o'))]
    if height>=60:
        assert sum(line.count('🌕') if width>1 else line.count('O') for line in moonlines)==65
        expected=30 if width>=60 else max(1,width//2)
        counts=[sum(line.count(c) for c in ('🌕','🌑')) if width>1 else len(line) for line in moonlines]
        assert counts==[expected]*(66//expected)+([66%expected] if 66%expected else []),(width,counts)
    results.append({'terminal':f'{width}x{height}','active_visible':True,'rows_fit':True,'moon_rows':moonlines})
(out/'terminal-results.json').write_text(json.dumps(results,ensure_ascii=False,indent=2))
print(json.dumps(results,ensure_ascii=False,indent=2))
