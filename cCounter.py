import Queue;

class cCounter(object):
  def __init__(oSelf, uValue = 0):
   oSelf.oValueQueue = Queue.Queue();
   oSelf.oValueQueue.put(uValue);
  
  @property
  def uValue(oSelf):
    uValue = oSelf.oValueQueue.get();
    oSelf.oValueQueue.put(uValue);
    return uValue;
  
  def fuIncrease(oSelf):
    return oSelf.fuAdd(1);
  def fuAdd(oSelf, uValue):
    uNewValue = oSelf.oValueQueue.get() + uValue;
    oSelf.oValueQueue.put(uNewValue);
    return uNewValue;
  
  def fuDecrease(oSelf):
    return oSelf.fuSubtract(1);
  def fuSubtract(oSelf, uValue):
    uNewValue = oSelf.oValueQueue.get() - uValue;
    oSelf.oValueQueue.put(uNewValue);
    return uNewValue;
