# LibreOffice UNO: open a docx, accept or reject all tracked changes, save as plain text.
import sys, uno, time, subprocess, os
from com.sun.star.beans import PropertyValue
def pv(n, v):
    p = PropertyValue(); p.Name = n; p.Value = v; return p
src, out, mode = sys.argv[1:4]
proc = subprocess.Popen(['soffice', '--headless', '--norestore', '--accept=socket,host=localhost,port=2002;urp;'])
ctx = None
for _ in range(60):
    try:
        local = uno.getComponentContext()
        res = local.ServiceManager.createInstanceWithContext('com.sun.star.bridge.UnoUrlResolver', local)
        ctx = res.resolve('uno:socket,host=localhost,port=2002;urp;StarOffice.ComponentContext'); break
    except Exception:
        time.sleep(1)
smgr = ctx.ServiceManager
desk = smgr.createInstanceWithContext('com.sun.star.frame.Desktop', ctx)
doc = desk.loadComponentFromURL(uno.systemPathToFileUrl(os.path.abspath(src)), '_blank', 0, (pv('Hidden', True),))
disp = smgr.createInstanceWithContext('com.sun.star.frame.DispatchHelper', ctx)
disp.executeDispatch(doc.getCurrentController().getFrame(), '.uno:AcceptAllTrackedChanges' if mode == 'accept' else '.uno:RejectAllTrackedChanges', '', 0, ())
doc.storeToURL(uno.systemPathToFileUrl(os.path.abspath(out)), (pv('FilterName', 'Text (encoded)'), pv('FilterOptions', 'UTF8')))
doc.close(True)
try: desk.terminate()
except Exception: pass
proc.wait(timeout=30)
