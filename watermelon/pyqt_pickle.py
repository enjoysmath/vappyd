import dill as pickle
from copy import deepcopy
import inspect



def determine_auto_pickleable_members(ob):
    auto_pickles = set()
    
    for member in inspect.getmembers(ob):
        name = member[0]
        if name == 'setCentralWidget':
            debug = True
        if name.startswith('set'):
            if callable(getattr(ob, name)):
                getter_name = ob.getter_from_setter(name)
                if hasattr(ob, getter_name) and getter_name != 'layout':
                    setter = None
                    try:
                        setter = getattr(ob, name)
                        getter = getattr(ob, getter_name)
                        setter(getter())
                    except Exception as e:
                        pass
                    else:
                        try:
                            if getter_name != 'layout':
                                data = pickle.dumps(getter())
                                setter(pickle.loads(data))
                                auto_pickles.add(getter_name)    
                            else:
                                debug_me = True
                        except Exception as e:
                            print('Cannot yet pickle:', str(e))
    print(auto_pickles)
