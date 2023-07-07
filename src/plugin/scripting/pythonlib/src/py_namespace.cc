/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <motor/plugin.scripting.pythonlib/stdafx.h>
#include <motor/meta/classinfo.meta.hh>
#include <motor/plugin.scripting.pythonlib/pythonlib.hh>
#include <py_namespace.hh>

namespace Motor { namespace Python {

PyMethodDef PyMotorNamespace::s_methodArray[]
    = {{"__dir__", &PyMotorNamespace::dir, METH_NOARGS, nullptr}, {nullptr, nullptr, 0, nullptr}};

PyTypeObject PyMotorNamespace::s_pyType = {{{0, nullptr}, 0},
                                           "py_motor.Namespace",
                                           sizeof(PyMotorNamespace),
                                           0,
                                           &PyMotorNamespace::dealloc,
                                           nullptr,
                                           &PyMotorNamespace::getattr,
                                           &PyMotorNamespace::setattr,
                                           nullptr,
                                           &PyMotorNamespace::repr,
                                           nullptr,
                                           nullptr,
                                           nullptr,
                                           nullptr,
                                           nullptr,
                                           nullptr,
                                           nullptr,
                                           nullptr,
                                           nullptr,
                                           Py_TPFLAGS_MOTOR_DEFAULT | Py_TPFLAGS_IS_ABSTRACT,
                                           "Wrapper class for the C++ Motor namespaces",
                                           nullptr,
                                           nullptr,
                                           nullptr,
                                           0,
                                           nullptr,
                                           nullptr,
                                           PyMotorNamespace::s_methods,
                                           nullptr,
                                           nullptr,
                                           PyMotorObject::s_pyTypePtr,
                                           nullptr,
                                           nullptr,
                                           nullptr,
                                           0,
                                           &PyMotorNamespace::init,
                                           nullptr,
                                           nullptr,
                                           nullptr,
                                           nullptr,
                                           nullptr,
                                           nullptr,
                                           nullptr,
                                           nullptr,
                                           nullptr,
                                           nullptr,
                                           0,
                                           nullptr,
                                           nullptr};

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
    auto*       self_ = static_cast< PyMotorNamespace* >(self);
    const auto& klass = self_->value.as< const Meta::Class& >();
    istring     name_(name);
    for(raw< const Meta::Object > o = klass.objects; o; o = o->next)
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
    auto*       self_ = static_cast< PyMotorObject* >(self);
    istring     name_(name);
    const auto& klass = self_->value.as< const Meta::Class& >();
    for(raw< const Meta::Object > ob = klass.objects; ob; ob = ob->next)
    {
        if(ob->name == name_)
        {
            if(ob->value.type().access != Meta::Type::Constness::Const)
            {
                Meta::ConversionCost c = distance(value, ob->value.type());
                if(c < Meta::ConversionCost::s_incompatible)
                {
                    auto* v = (Meta::Value*)malloca(sizeof(Meta::Value));
                    unpack(value, ob->value.type(), v);
                    ob->value = *v;
                    v->~Value();
                    freea(v);
                    return 0;
                }
                else
                {
                    s_library->m_PyErr_Format(
                        *s_library->m_PyExc_TypeError,
                        minitl::format< 1024 >(FMT("({0}).{1} is of type {2}"), self_->value.type(),
                                               name, ob->value.type()));
                    return -1;
                }
            }
            else
            {
                s_library->m_PyErr_Format(
                    *s_library->m_PyExc_TypeError,
                    minitl::format< 1024u >(FMT("{0}.{1} is const"), self_->value.type(), name));
                return -1;
            }
        }
    }
    s_library->m_PyErr_Format(
        *s_library->m_PyExc_AttributeError,
        minitl::format< 1024 >(FMT("{0} object has no attribute {1}"), self_->value.type(), name));
    return -1;
}

PyObject* PyMotorNamespace::dir(PyObject* self, PyObject* args)
{
    auto* self_ = static_cast< PyMotorObject* >(self);
    motor_forceuse(args);
    PyObject* result = s_library->m_PyList_New(0);
    if(!result) return nullptr;
    const auto&                     klass      = self_->value.as< const Meta::Class& >();
    Type_PyString_FromStringAndSize fromString = s_library->getVersion() >= 30
                                                     ? s_library->m_PyUnicode_FromStringAndSize
                                                     : s_library->m_PyString_FromStringAndSize;

    for(raw< const Meta::Object > o = klass.objects; o; o = o->next)
    {
        PyObject* str = fromString(o->name.c_str(), Py_ssize_t(o->name.size()));
        if(!str)
        {
            Py_DECREF(result);
            return nullptr;
        }
        if(s_library->m_PyList_Append(result, str) == -1)
        {
            Py_DECREF(str);
            Py_DECREF(result);
            return nullptr;
        }
        Py_DECREF(str);
    }
    return result;
}

PyObject* PyMotorNamespace::repr(PyObject* self)
{
    auto*              self_ = static_cast< PyMotorObject* >(self);
    const Meta::Value& v     = self_->value;
    const auto&        ns    = v.as< const Meta::Class& >();

    if(s_library->getVersion() >= 30)
    {
        return s_library->m_PyUnicode_FromFormat("[%s]", ns.name.c_str());
    }
    else
    {
        return s_library->m_PyString_FromFormat("[%s]", ns.name.c_str());
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
    result        = (*s_library->m_PyModule_AddObject)(module, "Motor", stealValue(nullptr, v));
    motor_assert(result >= 0, "unable to register type");
    motor_forceuse(result);
}

}}  // namespace Motor::Python
