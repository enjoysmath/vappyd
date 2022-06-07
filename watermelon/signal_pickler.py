from PyQt5.QtCore import QObject, pyqtBoundSignal
import inspect

class PickleableSignal(QObject):
    """
    Wrapper class for a single signal, returned by __getattribute__ method of SignalPickler.
    Supports, lambda, delegates, disconnection by string or by another reference / copy of the
    lambda or delegate.  Supports pickling of everything using the dill library.
    For pickling to work, sender must be pickleable on its own in the usual way.
    """
    
    Handle, Slot = range(2)
    
    def __init__(self, sender=None, signal=None, new=None):
        assert(isinstance(sender, SignalPickler))    # Requires inheritance to work
        super().__init__()
        if new is None: new = True
        if new:
            self._sender = sender
            self._signal = signal
            self._slotInfo = {}       # Keyed by string representing lambda or delegate name
    
    def __setstate__(self, data):
        """
        Standard pickle method design.  Includes slot info and connection state.
        """
        self.__init__(init=False)
        self._sender = data['sender']
        self._signal = data['signal']
        self._slotInfo = {}
        # PyQt5 is not pickle aware so we must reconnect the signals after unpickling and/or copying.
        for slot_id, (handle, slot) in data['slot info'].items():
            self.connect(slot)
            
    def __getstate__(self):
        """
        Standard pickle method design.  Includes slot info.
        """
        return {
            'sender' : self._sender,
            'signal' : self._signal,
            'slot info' : self._slotInfo,
        }
    
    def __deepcopy__(self, memo):
        """
        Standard deepcopy method design.  Includes slot info and connection state.
        """
        from copy import deepcopy
        copy = type(self)(new=False)
        memo[id(self)] = copy
        copy._sender = deepcopy(self._sender, memo)
        copy._signal = self._signal    # OK, since we treat _signal as an immutable string.
        copy._slotInfo = {}
        # Of course we need to create this copies own slot connections.
        for slot_id, (handle, slot) in self._slotInfo.items():
            copy.connect(slot)  
        return copy
    
    def connect(self, slot):
        """
        Allows a given slot signature to be connected once and only once.
        Returns the slot id to use for disconnecting; alternatively pass in the exact
        same lambda or delegate and that should do the trick.  Returns None if 
        that same lambda or delegate has already been added.
        """
        if not self._sender.is_signal_registered(self):
            self._sender.register_signal(self)
        slot_id = self.slot_id(slot)
        if slot_id not in self._slotInfo:
            self._slotInfo[slot_id] = (self._sender.pyqt_signal(self._signal).connect(slot), slot)
            return slot_id
        return None
    
    def emit(self, *args):
        self._sender.pyqt_signal(self._signal).emit(*args)
        
    def disconnect(self, slot):
        """
        Pass in a string for the delegate / lambda or the delegate lambda itself and we'll
        generate the canonical id ourself.
        """
        if not isinstance(slot, str):
            slot = self.slot_id(slot)
        handle = self._slotInfo[slot][self.Handle]
        self._sender.pyqt_signal(self._signal).disconnect(handle)
        del self._slotInfo[slot]   # Don't forget to delete its entry
    
    def signal_name(self):
        return self._signal
    
    def sender_obj(self):
        return self._sender
    
    def slot(self, slot_id):
        return self._slotInfo[slot_id][self.Slot]
            
    def slot_id(self, slot):
        """
        This is how we generated an identifier string given a slot.
        Putting your lambda on a line of its own and the ID becomes the lambda alone.  For example:
        item.positionChanged.connect(lambda p: do_something())
        will result in:
        "item.positionChanged.connect(lambda p: do_something())" as the slot ID.
        while:
        item.positionChanged.connect(
             lambda p: do_something()
        ) 
        will result in:
        "lambda p: do_something()" as the slot ID.
        Theoretically, you could do the first one and add in dummy data on the line.
        "a, b, item.positionChange.connect(...)"
        Thus you can tie in identifying contextual info should the need arise.
        """
        return inspect.getsource(slot).strip()
    
    def __contains__(self, slot):
        if not isinstance(slot, str):
            slot = self.slot_id(slot)
        return slot in self._slotInfo
    
    
class SignalPickler:
    """
    A mixin class that helps connect / disconnect slots to member signals and pickle them (using dill).
    It should go "GraphicsBase(QGraphicsObject, SignalPickler)" as far as base class ordering goes.
    I've never found the other way around to work without compiler error or unexplicable runtime crash.
    The same goes for other classes.  Qt's raw class first, then your mixin or QObject-derived class.
    """    
    def __init__(self):
        self._signals = {}
        
    def __setstate__(self, data):
        """
        Subclasses must call this class's __setstate__ in order to pickle signals.
        """
        self.__init__()
        self._signals = data['signals']
        
    def __getstate__(self):
        """
        Subclasses must also call this class's __getstate__ in order to pickle signals.
        """
        return {
            'signals' : self._signals
        }
    
    def __deepcopy__(self, memo):
        """
        Want your objects / widgets copy & pasteable?  Then also call this from a subclass's __deepcopy__ method.
        """
        copy = type(self)()
        memo[id(self)] = copy
        copy._signals = deepcopy(self._signals, memo)
        return copy
    
    def __getattribute__(self, attr):
        """
        Internally, this is what SignalPickler does.  Every time you ask for a signal from the sender object,
        for example: `sender.positionChanged.connect(foo)`, instead of returning sender.positionChanged it will
        return a SignalPickler object wrapping it.
        """
        res = super().__getattribute__(attr)
        if isinstance(res, pyqtBoundSignal):
            if attr in self._signals:
                return self._signals[attr]      # First check if the signal is already registered!
            return PickleableSignal(sender=self, signal=attr)
        return res    
    
    def register_signal(self, signal):
        """
        For internal use only, usually.
        """
        self._signals[signal.signal_name()] = signal
        
    def is_signal_registered(self, signal):
        """
        For internal use only, usually.
        """
        return signal.signal_name() in self._signals
    
    def pyqt_signal(self, name):
        return super().__getattribute__(name)