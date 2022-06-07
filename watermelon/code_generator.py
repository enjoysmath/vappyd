import inspect
from collections import OrderedDict

class Setter:
    def __init__(self, ob, setter):
        self._setter = setter
        self._ob = ob
        
    def __call__(self, *args, **kwargs):
        self._setter(*args, **kwargs)
        self._args = args
        self._kwargs = kwargs
        self._ob.register_setter_call(self)
        
    def args(self):
        return self._args
    
    def kwargs(self):
        return self._kwargs
    
    def setter_name(self):
        return self._setter.__name__
        

class CodeGenerator:
    def __new__(cls, *args, **kwargs):
        """
        Records the subclass's initialization parameters.  Important if trying to
        convert the object's cosntruction to static code.
        """
        ob = super(cls, cls).__new__(cls, *args, **kwargs)
        ob._initArgs = args               
        ob._initKwargs = kwargs
        return ob
    
    def __init__(self, new=None):
        if new is None: new = True
        self._module = self.__module__
        self._class = self.__class__.__name__
        self._setterCalls = OrderedDict()
        
    def generate_import(self):
        return (self._module, self._class)
    
    def generate_class_name(self):
        return self._module + '.' + self._class
        
    def literal_to_string(self, lit):
        """
        TODO: make this more robust, it won't work in all cases, for instance when
        ' or " is escaped.
        """
        if isinstance(lit, str):
            if "'" in lit:
                return '"' + lit + '"'
            return "'" + lit + "'"
        return str(lit)
    
    def register_setter_call(self, setter_ob):
        name = setter_ob.setter_name()
        if name not in self._setterCalls:
            self._setterCalls[name] = setter_ob
            
    def __getattribute__(self, attr):
        """
        """
        if __debug__:
            if attr.startswith('set'):
                getname = self.getter_from_setter(attr)
                if hasattr(self, getname):                    
                    if attr in self._setterCalls:  
                        # It's important that this start with something other than "set" to avoid oo recursion
                        return self._setterCalls[attr]
                    else:
                        return Setter(ob=self, setter=super().__getattribute__(attr))
        return super().__getattribute__(attr) 
    
    def generate_setter_call(self, ident, setter_ob, existing_vars=None):
        if existing_vars is None:
            existing_vars = set()
 
        code, arg_vars, kwarg_vars = self.generate_dependencies(setter_ob.args(), setter_ob.kwargs())
        
        code += ident + '.' + setter_ob.setter_name() + '('
        
        for var in arg_vars:
            code += var + ', '
        for keyword, var in kwarg_vars:
            code += keyword + '=' + var + ', '
        code = code[:-2] + ')\n'
            
        return code         
    
    def generate_dependencies(self, args, kwargs):
        code = ''
        arg_vars = []
        kwarg_vars = []
        
        for arg in args:
            if isinstance(arg, CodeGenerator):
                var, code = arg.generate_init(existing_vars, scope)
                init_code += code + '\n'
                arg_vars.append(var)
            else:
                arg_vars.append(self.literal_to_string(arg))
                
        for keyword, arg in kwargs.items():
            if isinstance(arg, CodeGenerator):
                var, code = arg.generate_init(existing_vars, scope)
                init_code += code + '\n'
                kwarg_vars.append((keyword, var))
            else:
                arg = self.literal_to_string(arg)
                kwarg_vars.append((keyword, self.literal_to_string(arg)))        
        
        return code, arg_vars, kwarg_vars
    
    def generate_init(self, existing_vars=None, scope=None):
        """
        Convert all dependencies into static init code.
        """
        if existing_vars is None:
            existing_vars = set()
        
        ident = self.generate_variable_name(existing_vars, scope)
        init_code, arg_vars, kwarg_vars = self.generate_dependencies(self._initArgs, self._initKwargs)
        init_code += ident + ' = ' + self.generate_class_name() + '('
        
        for var in arg_vars:
            init_code += var + ', '
        for keyword, var in kwarg_vars:
            init_code += keyword + '=' + var + ', '
            
        init_code = init_code[:-2] + ')\n'
        
        for setter_ob in self._setterCalls.values():
            init_code += self.generate_setter_call(ident, setter_ob, existing_vars)
            
        return ident, init_code 
        
    def generate_variable_name(self, existing_vars, scope=None):
        if scope is None:
            scope = ''
        else:
            scope += '.'                
        base_name = None
        if hasattr(self, 'objectName'):
            base_name = self.objectName()
        if not base_name:
            typ = type(self)
            base_name = typ.__name__
            base_name = base_name[0].lower() + base_name[1:]
        k = 1
        base_name = scope + base_name
        name = base_name
        while name in existing_vars:
            name = base_name + str(k)
            k += 1
        existing_vars.add(name)
        return name
