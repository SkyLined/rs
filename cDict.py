import Queue;

class cDict(object):
  def __init__(oSelf, dxValue = {}):
   oSelf.oValueQueue = Queue.Queue();
   oSelf.oValueQueue.put(dxValue);
  
  @property
  def uSize(oSelf):
    dxValue = oSelf.oValueQueue.get();
    try:
      return len(dxValue);
    finally:
      oSelf.oValueQueue.put(dxValue);
  
  @property
  def dxValue(oSelf):
    dxValue = oSelf.oValueQueue.get();
    try:
      return dict(dxValue);
    finally:
      oSelf.oValueQueue.put(dxValue);
  
  def fSet(oSelf, sName, xValue):
    dxValue = oSelf.oValueQueue.get();
    dxValue[sName] = xValue;
    oSelf.oValueQueue.put(dxValue);
  
  def fRemove(oSelf, sName):
    dxValue = oSelf.oValueQueue.get();
    del dxValue[sName];
    oSelf.oValueQueue.put(dxValue);
  
  def fbContains(oSelf, sName):
    dxValue = oSelf.oValueQueue.get();
    try:
      return sName in dxValue;
    finally:
      oSelf.oValueQueue.put(dxValue);


