import distutils.core
import Cython.Build
distutils.core.setup(
    ext_modules = Cython.Build.cythonize("classifier.pyx"))



#python c_python_setup.py build_ext --inplace