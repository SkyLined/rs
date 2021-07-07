import queue;

class cList(object):
  def __init__(oSelf, axValue = []):
   oSelf.oValueQueue = queue.Queue();
   oSelf.oValueQueue.put(axValue);
  
  @property
  def uSize(oSelf):
    axValue = oSelf.oValueQueue.get();
    try:
      return len(axValue);
    finally:
      oSelf.oValueQueue.put(axValue);
  
  @property
  def axValue(oSelf):
    axValue = oSelf.oValueQueue.get();
    try:
      return axValue[:];
    finally:
      oSelf.oValueQueue.put(axValue);
  
  def fAdd(oSelf, xValue):
    axValue = oSelf.oValueQueue.get();
    axValue.append(xValue);
    oSelf.oValueQueue.put(axValue);
  
  def fRemove(oSelf, xValue):
    axValue = oSelf.oValueQueue.get();
    axValue.remove(xValue);
    oSelf.oValueQueue.put(axValue);
  
  def fbContains(oSelf, xValue):
    axValue = oSelf.oValueQueue.get();
    try:
      return xValue in axValue;
    finally:
      oSelf.oValueQueue.put(axValue);


