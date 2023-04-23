/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#pragma once

#include <cstdio>

namespace Motor { namespace Python {

#ifdef _LP64
typedef i64 Py_ssize_t;
#else
typedef i32 Py_ssize_t;
#endif
typedef Py_ssize_t Py_hash_t;

struct PyThreadState;
struct PyObject;
struct PyTypeObject;
struct PyCodeObject;
struct PyMethodDef;
struct PyModuleDef;
struct PyMemberDef;
struct PyGetSetDef;
struct PyCompilerFlags;

typedef void (*Type_Py_SetPythonHome2)(const char* home);
typedef void (*Type_Py_SetPythonHome3)(const wchar_t* home);
typedef void (*Type_Py_InitializeEx)(int initsigs);
typedef void (*Type_Py_Finalize)();
typedef PyThreadState* (*Type_Py_NewInterpreter)();
typedef void (*Type_Py_EndInterpreter)(PyThreadState* tstate);
typedef const char* (*Type_Py_GetPath)();
typedef const char* (*Type_Py_GetVersion)();
typedef PyObject* (*Type_Py_InitModule4)(const char* name, PyMethodDef* methods, const char* doc,
                                         PyObject* self, int apiver);
typedef PyObject* (*Type_Py_InitModule4_64)(const char* name, PyMethodDef* methods, const char* doc,
                                            PyObject* self, int apiver);

typedef PyObject* (*Type_PyModule_Create2)(PyModuleDef* module, int apiver);
typedef int (*Type_PyModule_AddObject)(PyObject* module, const char* name, PyObject* value);
typedef PyObject* (*Type_PyModule_GetDict)(PyObject* module);
typedef PyObject* (*Type_PyImport_AddModule)(const char* module);
typedef int (*Type_PyImport_AppendInittab2)(const char* name, void (*)());
typedef int (*Type_PyImport_AppendInittab3)(const char* name, PyObject* (*)());

typedef void (*Type_PyEval_InitThreads)();
typedef PyThreadState* (*Type_PyEval_SaveThread)();
typedef void (*Type_PyEval_AcquireThread)(PyThreadState* tstate);
typedef void (*Type_PyEval_ReleaseThread)(PyThreadState* tstate);
typedef void (*Type_PyEval_ReleaseLock)();
typedef PyThreadState* (*Type_PyThreadState_Swap)(PyThreadState* tstate);

typedef int (*Type_PyRun_SimpleString)(const char* command);
typedef int (*Type_PyRun_InteractiveLoopFlags)(FILE* fp, const char* filename,
                                               PyCompilerFlags* flags);
typedef PyCodeObject* (*Type_Py_CompileStringFlags)(const char* str, const char* filename,
                                                    int start, PyCompilerFlags* flags);
typedef PyCodeObject* (*Type_Py_CompileStringExFlags)(const char* str, const char* filename,
                                                      int start, PyCompilerFlags* flags,
                                                      int optimize);
typedef PyObject* (*Type_PyEval_EvalCodeEx)(PyCodeObject* co, PyObject* globals, PyObject* locals,
                                            PyObject** args, int argcount, PyObject** kws,
                                            int kwcount, PyObject** defs, int defcount,
                                            PyObject* closure);

typedef PyObject* (*PyCFunction)(PyObject* self, PyObject* args);

typedef PyObject* (*unaryfunc)(PyObject*);
typedef PyObject* (*binaryfunc)(PyObject*, PyObject*);
typedef PyObject* (*ternaryfunc)(PyObject*, PyObject*, PyObject*);
typedef Py_ssize_t (*lenfunc)(PyObject*);
typedef PyObject* (*ssizeargfunc)(PyObject*, Py_ssize_t);
typedef PyObject* (*ssizessizeargfunc)(PyObject*, Py_ssize_t, Py_ssize_t);
typedef int (*ssizeobjargproc)(PyObject*, Py_ssize_t, PyObject*);
typedef int (*ssizessizeobjargproc)(PyObject*, Py_ssize_t, Py_ssize_t, PyObject*);
typedef int (*objobjargproc)(PyObject*, PyObject*, PyObject*);

typedef int (*visitproc)(PyObject* object, void* arg);
typedef int (*traverseproc)(PyObject* self, visitproc visit, void* arg);
typedef int (*inquiry)(PyObject* self);
typedef void (*freefunc)(void*);
typedef void (*destructor)(PyObject*);
typedef int (*printfunc)(PyObject*, FILE*, int);
typedef int (*cmpfunc)(PyObject*, PyObject*);
typedef PyObject* (*reprfunc)(PyObject*);
typedef void (*freefunc)(void*);
typedef PyObject* (*getattrfunc)(PyObject*, const char*);
typedef PyObject* (*getattrofunc)(PyObject*, PyObject*);
typedef int (*setattrfunc)(PyObject*, const char*, PyObject*);
typedef int (*setattrofunc)(PyObject*, PyObject*, PyObject*);
typedef Py_hash_t (*hashfunc)(PyObject*);
typedef PyObject* (*richcmpfunc)(PyObject*, PyObject*, int);
typedef PyObject* (*getiterfunc)(PyObject*);
typedef PyObject* (*iternextfunc)(PyObject*);
typedef PyObject* (*descrgetfunc)(PyObject*, PyObject*, PyObject*);
typedef int (*descrsetfunc)(PyObject*, PyObject*, PyObject*);
typedef int (*initproc)(PyObject*, PyObject*, PyObject*);
typedef int (*objobjproc)(PyObject*, PyObject*);
typedef int (*coercion)(PyObject**, PyObject**);
typedef PyObject* (*newfunc)(PyTypeObject*, PyObject*, PyObject*);
typedef PyObject* (*allocfunc)(PyTypeObject*, Py_ssize_t);
typedef PyObject* (*vectorcallfunc)(PyObject*, PyObject* const*, Py_ssize_t, PyObject*);

typedef int (*Type_PyObject_SetAttrString)(PyObject* o, const char* name, PyObject* value);
typedef PyObject* (*Type_PyObject_GetAttrString)(PyObject* o, const char* name);
typedef int (*Type__PyArg_ParseTuple_SizeT)(             // NOLINT(bugprone-reserved-identifier)
    PyObject* args, const char* format, ...);
typedef int (*Type__PyArg_ParseTupleAndKeywords_SizeT)(  // NOLINT(bugprone-reserved-identifier)
    PyObject* args, PyObject* kw, const char* format, char** kws, ...);
typedef int (*Type_PyType_Ready)(PyTypeObject* type);
typedef PyObject* (*Type_PyType_GenericAlloc)(PyTypeObject* type, Py_ssize_t size);
typedef PyObject* (*Type_PyType_GenericNew)(PyTypeObject* type, PyObject* args, PyObject* kwargs);
typedef int (*Type_PyObject_IsTrue)(PyObject* arg);
typedef PyObject* (*Type_PyCFunction_NewEx)(PyMethodDef* method, PyObject* self, PyObject* module);

typedef PyObject* (*Type_PyList_New)(Py_ssize_t len);
typedef Py_ssize_t (*Type_PyList_Size)(PyObject* list);
typedef PyObject* (*Type_PyList_GetItem)(PyObject* list, Py_ssize_t index);
typedef int (*Type_PyList_SetItem)(PyObject* list, Py_ssize_t index, PyObject* item);
typedef int (*Type_PyList_Insert)(PyObject* list, Py_ssize_t index, PyObject* item);
typedef int (*Type_PyList_Append)(PyObject* list, PyObject* item);
typedef PyObject* (*Type_PyList_GetSlice)(PyObject* list, Py_ssize_t low, Py_ssize_t high);
typedef int (*Type_PyList_SetSlice)(PyObject* list, Py_ssize_t low, Py_ssize_t high,
                                    PyObject* itemlist);

typedef PyObject* (*Type_PyTuple_New)(Py_ssize_t len);
typedef Py_ssize_t (*Type_PyTuple_Size)(PyObject* tuple);
typedef PyObject* (*Type_PyTuple_GetItem)(PyObject* tuple, Py_ssize_t index);
typedef int (*Type_PyTuple_SetItem)(PyObject* list, Py_ssize_t index, PyObject* item);
typedef PyObject* (*Type_PyTuple_GetSlice)(PyObject* list, Py_ssize_t low, Py_ssize_t high);

typedef PyObject* (*Type_PyDict_New)();
typedef Py_ssize_t (*Type_PyDict_Size)(PyObject* dict);
typedef PyObject* (*Type_PyDict_GetItem)(PyObject* dict, PyObject* key);
typedef int (*Type_PyDict_SetItem)(PyObject* dict, PyObject* key, PyObject* item);
typedef int (*Type_PyDict_DelItem)(PyObject* dict, PyObject* key);
typedef int (*Type_PyDict_Next)(PyObject* dict, Py_ssize_t* pos, PyObject** key, PyObject** item);
typedef PyObject* (*Type_PyDict_GetItemString)(PyObject* dict, const char* key);
typedef int (*Type_PyDict_SetItemString)(PyObject* dict, const char* key, PyObject* value);
typedef PyObject* (*Type_PyString_FromString)(const char* v);
typedef PyObject* (*Type_PyString_FromStringAndSize)(const char* v, Py_ssize_t len);
typedef PyObject* (*Type_PyString_FromFormat)(const char* format, ...);
typedef Py_ssize_t (*Type_PyString_Size)(PyObject* string);
typedef char* (*Type_PyString_AsString)(PyObject* string);
typedef int (*Type_PyString_AsStringAndSize)(PyObject* obj, char** buffer, Py_ssize_t* length);

typedef PyObject* (*Type_PyUnicode_FromString)(const char* v);
typedef PyObject* (*Type_PyUnicode_FromStringAndSize)(const char* v, Py_ssize_t len);
typedef PyObject* (*Type_PyUnicode_FromFormat)(const char* format, ...);
typedef char* (*Type_PyUnicode_AsUTF8)(PyObject* unicode);
typedef PyObject* (*Type_PyUnicode_AsASCIIString)(PyObject* unicode);
typedef PyObject* (*Type_PyUnicode_AsUTF8String)(PyObject* unicode);
typedef char* (*Type_PyBytes_AsString)(PyObject* bytes);

typedef int (*Type_PyBool_Check)(PyObject* boolobject);
typedef PyObject* (*Type_PyBool_FromLong)(long value);
typedef PyObject* (*Type_PyInt_FromLong)(long value);
typedef unsigned long (*Type_PyInt_AsUnsignedLongMask)(PyObject* intobject);
typedef PyObject* (*Type_PyLong_FromUnsignedLongLong)(unsigned long long value);
typedef unsigned long long (*Type_PyLong_AsUnsignedLongLongMask)(PyObject* longobject);
typedef PyObject* (*Type_PyFloat_FromDouble)(double value);
typedef double (*Type_PyFloat_AsDouble)(PyObject* doubleobject);
typedef PyObject* Type__Py_NoneStruct;            // NOLINT(bugprone-reserved-identifier)
typedef PyObject* Type__Py_TrueStruct;            // NOLINT(bugprone-reserved-identifier)
typedef PyObject* Type__Py_FalseStruct;           // NOLINT(bugprone-reserved-identifier)
typedef PyObject* Type__Py_NotImplementedStruct;  // NOLINT(bugprone-reserved-identifier)

typedef void (*Type_PyErr_Print)();
typedef void (*Type_PyErr_SetString)(PyTypeObject* errorType, const char* message);
typedef PyObject* (*Type_PyErr_Format)(PyTypeObject* errorType, const char* format, ...);
typedef int (*Type_PyErr_BadArgument)();

typedef PyTypeObject*  Type_PyBool_Type;
typedef PyTypeObject*  Type_PyFloat_Type;
typedef PyTypeObject** Type_PyExc_Exception;
typedef PyTypeObject** Type_PyExc_AttributeError;
typedef PyTypeObject** Type_PyExc_ImportError;
typedef PyTypeObject** Type_PyExc_IndexError;

typedef PyTypeObject** Type_PyExc_TypeError;

typedef PyObject* (*Type_PySys_GetObject)(const char* nam);
typedef int (*Type_PySys_SetObject)(const char* name, PyObject* object);

struct PyObject
{
    minitl::size_type py_refcount {};
    PyTypeObject*     py_type {};
};

enum Py_InputStart
{
    Py_single_input = 256,
    Py_file_input   = 257,
    Py_eval_input   = 258
};

struct PyVarObject
{
    PyObject   object;
    Py_ssize_t ob_size {};
};

#define Py_TPFLAGS_HAVE_GETCHARBUFFER (1L << 0)
#define Py_TPFLAGS_HAVE_SEQUENCE_IN   (1L << 1)
#define Py_TPFLAGS_HAVE_INPLACEOPS    (1L << 3)
#define Py_TPFLAGS_CHECKTYPES         (1L << 4)
#define Py_TPFLAGS_HAVE_RICHCOMPARE   (1L << 5)
#define Py_TPFLAGS_HAVE_WEAKREFS      (1L << 6)
#define Py_TPFLAGS_HAVE_ITER          (1L << 7)
#define Py_TPFLAGS_HAVE_CLASS         (1L << 8)
#define Py_TPFLAGS_HEAPTYPE           (1L << 9)
#define Py_TPFLAGS_BASETYPE           (1L << 10)
#define Py_TPFLAGS_READY              (1L << 12)
#define Py_TPFLAGS_READYING           (1L << 13)
#define Py_TPFLAGS_HAVE_GC            (1L << 14)

#define Py_TPFLAGS_HAVE_INDEX        (1L << 17)
#define Py_TPFLAGS_HAVE_VERSION_TAG  (1L << 18)
#define Py_TPFLAGS_VALID_VERSION_TAG (1L << 19)
#define Py_TPFLAGS_IS_ABSTRACT       (1L << 20)
#define Py_TPFLAGS_HAVE_NEWBUFFER    (1L << 21)

/* These flags are used to determine if a type is a subclass. */
#define Py_TPFLAGS_INT_SUBCLASS      (1L << 23)
#define Py_TPFLAGS_LONG_SUBCLASS     (1L << 24)
#define Py_TPFLAGS_LIST_SUBCLASS     (1L << 25)
#define Py_TPFLAGS_TUPLE_SUBCLASS    (1L << 26)
#define Py_TPFLAGS_STRING_SUBCLASS   (1L << 27)
#define Py_TPFLAGS_UNICODE_SUBCLASS  (1L << 28)
#define Py_TPFLAGS_DICT_SUBCLASS     (1L << 29)
#define Py_TPFLAGS_BASE_EXC_SUBCLASS (1L << 30)
#define Py_TPFLAGS_TYPE_SUBCLASS     (1L << 31)

#define Py_TPFLAGS_MOTOR_DEFAULT 0

struct PyTypeObject
{
    struct PyNumberMethods
    {
        binaryfunc nb_add;
        binaryfunc nb_subtract;
        binaryfunc nb_multiply;
    };

    struct Py2NumberMethods
    {
        PyNumberMethods nb_common;
        binaryfunc      nb_divide;
        binaryfunc      nb_remainder;
        binaryfunc      nb_divmod;
        ternaryfunc     nb_power;
        unaryfunc       nb_negative;
        unaryfunc       nb_positive;
        unaryfunc       nb_absolute;
        inquiry         nb_nonzero;
        unaryfunc       nb_invert;
        binaryfunc      nb_lshift;
        binaryfunc      nb_rshift;
        binaryfunc      nb_and;
        binaryfunc      nb_xor;
        binaryfunc      nb_or;
        coercion        nb_coerce;
        unaryfunc       nb_int;
        unaryfunc       nb_long;
        unaryfunc       nb_float;
        unaryfunc       nb_oct;
        unaryfunc       nb_hex;

        binaryfunc  nb_inplace_add;
        binaryfunc  nb_inplace_subtract;
        binaryfunc  nb_inplace_multiply;
        binaryfunc  nb_inplace_divide;
        binaryfunc  nb_inplace_remainder;
        ternaryfunc nb_inplace_power;
        binaryfunc  nb_inplace_lshift;
        binaryfunc  nb_inplace_rshift;
        binaryfunc  nb_inplace_and;
        binaryfunc  nb_inplace_xor;
        binaryfunc  nb_inplace_or;

        /* The following require the Py_TPFLAGS_HAVE_CLASS flag */
        binaryfunc nb_floor_divide;
        binaryfunc nb_true_divide;
        binaryfunc nb_inplace_floor_divide;
        binaryfunc nb_inplace_true_divide;

        unaryfunc nb_index;
    };

    struct Py3NumberMethods
    {
        PyNumberMethods nb_common;
        binaryfunc      nb_remainder;
        binaryfunc      nb_divmod;
        ternaryfunc     nb_power;
        unaryfunc       nb_negative;
        unaryfunc       nb_positive;
        unaryfunc       nb_absolute;
        inquiry         nb_bool;
        unaryfunc       nb_invert;
        binaryfunc      nb_lshift;
        binaryfunc      nb_rshift;
        binaryfunc      nb_and;
        binaryfunc      nb_xor;
        binaryfunc      nb_or;
        unaryfunc       nb_int;
        void*           nb_reserved; /* the slot formerly known as nb_long */
        unaryfunc       nb_float;

        binaryfunc  nb_inplace_add;
        binaryfunc  nb_inplace_subtract;
        binaryfunc  nb_inplace_multiply;
        binaryfunc  nb_inplace_remainder;
        ternaryfunc nb_inplace_power;
        binaryfunc  nb_inplace_lshift;
        binaryfunc  nb_inplace_rshift;
        binaryfunc  nb_inplace_and;
        binaryfunc  nb_inplace_xor;
        binaryfunc  nb_inplace_or;

        binaryfunc nb_floor_divide;
        binaryfunc nb_true_divide;
        binaryfunc nb_inplace_floor_divide;
        binaryfunc nb_inplace_true_divide;

        unaryfunc nb_index;

        binaryfunc nb_matrix_multiply;
        binaryfunc nb_inplace_matrix_multiply;
    };

    struct PySequenceMethods
    {
        lenfunc              sq_length;
        binaryfunc           sq_concat;
        ssizeargfunc         sq_repeat;
        ssizeargfunc         sq_item;
        ssizessizeargfunc    sq_slice;
        ssizeobjargproc      sq_ass_item;
        ssizessizeobjargproc sq_ass_slice;
        objobjproc           sq_contains;
        binaryfunc           sq_inplace_concat;
        ssizeargfunc         sq_inplace_repeat;
    };

    struct PyMappingMethods
    {
        lenfunc       mp_length;
        binaryfunc    mp_subscript;
        objobjargproc mp_ass_subscript;
    };

    PyVarObject       object;
    const char*       tp_name {};
    minitl::size_type tp_basicsize {};
    minitl::size_type tp_itemsize {};

    destructor  tp_dealloc {};
    printfunc   tp_print {};
    getattrfunc tp_getattr {};
    setattrfunc tp_setattr {};
    cmpfunc     tp_compare {};
    reprfunc    tp_repr {};

    PyNumberMethods*   tp_as_number {};
    PySequenceMethods* tp_as_sequence {};
    PyMappingMethods*  tp_as_mapping {};

    hashfunc     tp_hash {};
    ternaryfunc  tp_call {};
    reprfunc     tp_str {};
    getattrofunc tp_getattro {};
    setattrofunc tp_setattro {};

    void* tp_as_buffer {};

    unsigned long tp_flags {};

    const char*   tp_doc {};
    traverseproc  tp_traverse {};
    inquiry       tp_clear {};
    richcmpfunc   tp_richcompare {};
    Py_ssize_t    tp_weaklistoffset {};
    getiterfunc   tp_iter {};
    iternextfunc  tp_iternext {};
    PyMethodDef*  tp_methods {};
    PyMemberDef*  tp_members {};
    PyGetSetDef*  tp_getset {};
    PyTypeObject* tp_base {};
    PyObject*     tp_dict {};
    descrgetfunc  tp_descr_get {};
    descrsetfunc  tp_descr_set {};
    Py_ssize_t    tp_dictoffset {};
    initproc      tp_init {};
    allocfunc     tp_alloc {};
    newfunc       tp_new {};
    freefunc      tp_free {};
    inquiry       tp_is_gc {};
    PyObject*     tp_bases {};
    PyObject*     tp_mro {};
    PyObject*     tp_cache {};
    PyObject*     tp_subclasses {};
    PyObject*     tp_weaklist {};
    destructor    tp_del {};

    unsigned int tp_version_tag {};
    destructor   tp_finalize {};

    /* Python 3.9 */
    vectorcallfunc tp_vectorcall {};
};

struct PyMethodDef
{
    const char* const name {};
    PyCFunction       method {};
    int               flags {};
    const char* const doc {};
};

/* Flag passed to newmethodobject */
#define METH_OLDARGS  0x0000
#define METH_VARARGS  0x0001
#define METH_KEYWORDS 0x0002
/* METH_NOARGS and METH_O must not be combined with the flags above. */
#define METH_NOARGS 0x0004
#define METH_O      0x0008
/* METH_CLASS and METH_STATIC are a little different; these control
   the construction of methods for a class.  These cannot be used for
   functions in modules. */
#define METH_CLASS  0x0010
#define METH_STATIC 0x0020
/* METH_COEXIST allows a method to be entered eventhough a slot has
   already filled the entry.  When defined, the flag allows a separate
   method, "__contains__" for example, to coexist with a defined
   slot like sq_contains. */
#define METH_COEXIST 0x0040

struct PyModuleDef_Base
{
    PyObject ob_base;
    PyObject* (*m_init)() {};
    minitl::size_type m_index {};
    PyObject*         m_copy {};
};

#define PyModuleDef_HEAD_INIT                                                                      \
    {                                                                                              \
        {1, NULL}, /* ob_base */                                                                   \
            NULL,  /* m_init */                                                                    \
            0,     /* m_index */                                                                   \
            NULL,  /* m_copy */                                                                    \
    }

struct PyModuleDef
{
    PyModuleDef_Base  m_base;
    const char*       m_name {};
    const char*       m_doc {};
    minitl::size_type m_size {};
    PyMethodDef*      m_methods {};
    inquiry           m_reload {};
    traverseproc      m_traverse {};
    inquiry           m_clear {};
    freefunc          m_free {};
};

#define Py_INCREF(pyobject)                                                                        \
    do                                                                                             \
    {                                                                                              \
        Motor::Python::PyObject* o_ = reinterpret_cast< Motor::Python::PyObject* >(pyobject);      \
        ++o_->py_refcount;                                                                         \
    } while(0)
#define Py_DECREF(pyobject)                                                                        \
    do                                                                                             \
    {                                                                                              \
        Motor::Python::PyObject* o_ = reinterpret_cast< Motor::Python::PyObject* >(pyobject);      \
        if(--o_->py_refcount == 0)                                                                 \
        {                                                                                          \
            o_->py_type->tp_dealloc(o_);                                                           \
        }                                                                                          \
    } while(0)

}}  // namespace Motor::Python
