exec(open('.live-renderer/check.py').read().split('results=[]')[0])
Path('.live-renderer/base-drive.mjs').write_text(Path('.live-renderer/drive.mjs').read_text().replace("'./renderer.mjs'","'../.live-baseline/baseline.mjs'"))
def run(file,w,h):
 m,s=pty.openpty();fcntl.ioctl(s,termios.TIOCSWINSZ,struct.pack('HHHH',h,w,0,0))
 p=subprocess.Popen(['node',file],stdin=s,stdout=s,stderr=s);os.close(s);data=b''
 while True:
  try:
   b=os.read(m,65536)
   if not b:break
   data+=b
  except OSError:break
 os.close(m);assert p.wait()==0
 return data
records=[]
for w in (63,80):
 old=run('.live-renderer/base-drive.mjs',w,60);new=run('.live-renderer/drive.mjs',w,60)
 assert old==new
 records.append(f'{w}x60: complete real Renderer terminal output byte-identical to base commit (fixed clock and star seed).')
(out/'default-comparison.txt').write_text('\n'.join(records)+'\n')
print('\n'.join(records))
