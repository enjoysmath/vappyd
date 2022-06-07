import inspect

class CodeGenerator:
    def __new__(cls, *args, **kwargs):
        """
        Records the subclass's initialization parameters.  Important if trying to
        convert the object's cosntruction to static code.
        """
        self._initArgs = args               
        self._initKwargs = kwargs
        return cls(args, kwargs)
    
    def __init__(self, new=None):
        if new is None: new = True
        self._module = self.__module__
        self._class = self.__class__.__name__
        
    def generate_import(self):
        return (self._module, self._class)
    
    def generate_class_name(self):
        return self._module + '.' + self._class
        
    def generate_init(self, existing_vars=None, var=None):
        """
        Convert all dependencies into static init code.
        """
        if existing_vars is None:
            existing_vars = set()
        var = self.generate_variable_name(type(self), existing_vars)
        
        init_code = ''
        arg_vars = []
        kwarg_vars = []
        
        for arg in self._initArgs:
            if isinstance(arg, CodeGenerator):
                var, code = arg.generate_init(existing_vars)
                init_code += code + '\n'
                arg_vars.append(var)
            else:
                arg_vars.append(str(arg))
                
        for keyword, arg in self._initKwargs.items():
            if isinstance(arg, CodeGenerator):
                var, code = arg.generate_init(existing_vars)
                init_code += code 
                kwarg_vars.append((keyword, var))
            else:
                kwarg_vars.append((keyword, str(arg)))
        
        init_code += var + ' = ' + self.generate_class_name() + '('
        for var in arg_vars:
            init_code += var + ', '
        for keyword, var in kwarg_vars:
            init_code += keyword + '=' + var + ', '
        init_code = init_code[2:] + ')'
        init_code += '\n'
        return var, init_code 
        
    def generate_variable_name(self, typ, existing_vars):
        base_name = typ.__name__
        base_name = base_name[0].lower() + base_name[1:]
        k = 1
        name = base_name
        while name in existing_vars:
            name = base_name + str(k)
            k += 1
        existing_vars.add(name)
        return name
        
 