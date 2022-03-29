/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <motor/plugin.scripting.pythonlib/stdafx.h>
#include <motor/meta/classinfo.meta.hh>
#include <motor/plugin.scripting.pythonlib/pythonlib.hh>
#include <py_namespace.hh>

namespace Motor { namespace Python {

PyMethodDef PyMotorNamespace::s_methods[]
    = {{"__dir__", &PyMotorNamespace::dir, METH_NOARGS, NULL}, {NULL, NULL, 0, NULL}};

PyTypeObject PyMotorNamespace::s_pyType = {{{0, 0}, 0},
                                           "py_motor.Namespace",
                                           sizeof(PyMotorNamespace),
                                           0,
                                           &PyMotorNamespace::dealloc,
                                           0,
                                           &PyMotorNamespace::getattr,
                                           &PyMotorNamespace::setattr,
                                           0,
                                           &PyMotorNamespace::repr,
                                           0,
                                           0,
                                           0,
                                           0,
                                           0,
                                           0,
                                           0,
                                           0,
                                           0,
                                           Py_TPFLAGS_MOTOR_DEFAULT | Py_TPFLAGS_IS_ABSTRACT,
                                           "Wrapper class for the C++ Motor namespaces",
                                           0,
                                           0,
                                           0,
                                           0,
                                           0,
                                           0,
                                           PyMotorNamespace::s_methods,
                                           0,
                                           0,
                                           &PyMotorObject::s_pyType,
                                           0,
                                           0,
                                           0,
                                           0,
                                           &PyMotorNamespace::init,
                                           0,
                                           0,
                                           0,
                                           0,
                                           0,
                                           0,
                                           0,
                                           0,
                                           0,
                                           0,
                                           0,
                                           0,
                                           0};

PyObject* PyMotorNamespace::stealValue(PyObject* owner, Meta::Value& value)
{
    motor_assert(value.type().metaclass->type() == Meta::ClassType_Namespace,
                 "PyMotorNamespace only accepts Namespace types");
    PyObject* result                                = s_pyType.tp_alloc(&s_pyType, 0);
    static_cast< PyMotorNamespace* >(result)->owner = owner;

    if(owner)
    {
        Py_INCREF(owner);
    }
    new(&(static_cast< PyMotorNamespace* >(result))->value) Meta::Value();
    (static_cast< PyMotorNamespace* >(result))->value.swap(value);
    return result;
}

int PyMotorNamespace::init(PyObject* self, PyObject* args, PyObject* kwds)
{
    /* todo */
    motor_forceuse(self);
    motor_forceuse(args);
    motor_forceuse(kwds);
    return 0;
}

PyObject* PyMotorNamespace::getattr(PyObject* self, const char* name)
{
    PyMotorNamespace*  self_ = static_cast< PyMotorNamespace* >(self);
    const Meta::Class& klass = self_->value.as< const Meta::Class& >();
    istring            name_(name);
    for(raw< const Meta::ObjectInfo > o = klass.objects; o; o = o->next)
    {
        if(o->name == name_)
        {
            Meta::Value v = o->value;
            return PyMotorObject::stealValue(self, v);
        }
    }
    return PyMotorObject::getattr(self, name);
}

int PyMotorNamespace::setattr(PyObject* self, const char* name, PyObject* value)
{
    PyMotorObject*     self_ = static_cast< PyMotorObject* >(self);
    istring            name_(name);
    const Meta::Class& klass = self_->value.as< const Meta::Class& >();
    for(raw< const Meta::ObjectInfo > ob = klass.objects; ob; ob = ob->next)
    {
        if(ob->name == name_)
        {
            if(ob->value.type().access != Meta::Type::Const)
            {
                Meta::ConversionCost c = distance(value, ob->value.type());
                if(c < Meta::ConversionCost::s_incompatible)
                {
                    Meta::Value* v = (Meta::Value*)malloca(sizeof(Meta::Value));
                    unpack(value, ob->value.type(), v);
                    ob->value = *v;
                    v->~Value();
                    freea(v);
                    return 0;
                }
                else
                {
                    s_library->m_PyErr_Format(*s_library->m_PyExc_TypeError, "%s.%s is of type %s",
                                              self_->value.type().name().c_str(), name,
                                              ob->value.type().name().c_str());
                    return -1;
                }
            }
            else
            {
                s_library->m_PyErr_Format(*s_library->m_PyExc_TypeError, "%s.%s is const",
                                          self_->value.type().name().c_str(), name);
                return -1;
            }
        }
    }
    s_library->m_PyErr_Format(*s_library->m_PyExc_AttributeError, "%s object has no attribute %s",
                              self_->value.type().name().c_str(), name);
    return -1;
}

PyObject* PyMotorNamespace::dir(PyObject* self, PyObject* args)
{
    PyMotorObject* self_ = static_cast< PyMotorObject* >(self);
    motor_forceuse(args);
    PyObject* result = s_library->m_PyList_New(0);
    if(!result) return NULL;
    const Meta::Class&             klass      = self_->value.as< const Meta::Class& >();
    PyString_FromStringAndSizeType fromString = s_library->getVersion() >= 30
                                                    ? s_library->m_PyUnicode_FromStringAndSize
                                                    : s_library->m_PyString_FromStringAndSize;

    for(raw< const Meta::ObjectInfo > o = klass.objects; o; o = o->next)
    {
        PyObject* str = fromString(o->name.c_str(), o->name.size());
        if(!str)
        {
            Py_DECREF(result);
            return NULL;
        }
        if(s_library->m_PyList_Append(result, str) == -1)
        {
            Py_DECREF(str);
            Py_DECREF(result);
            return NULL;
        }
        Py_DECREF(str);
    }
    return result;
}

PyObject* PyMotorNamespace::repr(PyObject* self)
{
    PyMotorObject*     self_ = static_cast< PyMotorObject* >(self);
    const Meta::Value& v     = self_->value;
    const Meta::Class& ns    = v.as< const Meta::Class& >();

    if(s_library->getVersion() >= 30)
    {
        return s_library->m_PyUnicode_FromFormat("[%s]", ns.fullname().str().name);
    }
    else
    {
        return s_library->m_PyString_FromFormat("[%s]", ns.fullname().str().name);
    }
}

void PyMotorNamespace::registerType(PyObject* module)
{
    int result = s_library->m_PyType_Ready(&s_pyType);
    motor_assert(result >= 0, "unable to register type");
    Py_INCREF(&s_pyType);
    result = (*s_library->m_PyModule_AddObject)(module, "Namespace", (PyObject*)&s_pyType);
    motor_assert(result >= 0, "unable to register type");
    Meta::Value v = Meta::Value(motor_motor_Namespace());
    result        = (*s_library->m_PyModule_AddObject)(module, "Motor", stealValue(0, v));
    motor_assert(result >= 0, "unable to register type");
    motor_forceuse(result);
}

}}  // namespace Motor::Python
