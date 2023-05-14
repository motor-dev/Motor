/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <motor/plugin.scripting.pythonlib/stdafx.h>
#include <motor/plugin.scripting.pythonlib/pythonlib.hh>
#include <py_object.hh>
#include <py_plugin.hh>

namespace Motor { namespace Python {

static PyTypeObject s_motorPluginType = {{{0, nullptr}, 0},
                                         "py_motor.Plugin",
                                         sizeof(PyMotorPlugin),
                                         0,
                                         &PyMotorPlugin::dealloc,
                                         nullptr,
                                         &PyMotorPlugin::getattr,
                                         &PyMotorPlugin::setattr,
                                         nullptr,
                                         &PyMotorPlugin::repr,
                                         nullptr,
                                         nullptr,
                                         nullptr,
                                         nullptr,
                                         nullptr,
                                         nullptr,
                                         nullptr,
                                         nullptr,
                                         nullptr,
                                         Py_TPFLAGS_MOTOR_DEFAULT,
                                         "Wrapper class for the C++ class Motor::Plugin::Plugin",
                                         nullptr,
                                         nullptr,
                                         nullptr,
                                         0,
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
                                         &PyMotorPlugin::init,
                                         nullptr,
                                         &PyMotorPlugin::create,
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

PyObject* PyMotorPlugin::create(PyTypeObject* type, PyObject* /*args*/, PyObject* /*kwds*/)
{
    auto* self = reinterpret_cast< PyMotorPlugin* >(type->tp_alloc(type, 0));
    new(&self->value) Plugin::Plugin< void >();
    return reinterpret_cast< PyObject* >(self);
}

int PyMotorPlugin::init(PyObject* self, PyObject* args, PyObject* /*kwds*/)
{
    auto*       self_ = reinterpret_cast< PyMotorPlugin* >(self);
    const char* name  = nullptr;
    if(s_library->m__PyArg_ParseTuple_SizeT(args, "s", &name))
    {
        self_->value = Plugin::Plugin< void >(inamespace(name), Plugin::Plugin< void >::Preload);
        return 0;
    }
    else
    {
        return -1;
    }
}

PyObject* PyMotorPlugin::getattr(PyObject* self, const char* name)
{
    auto* self_ = reinterpret_cast< PyMotorPlugin* >(self);
    if(self_->value)
    {
        Meta::Value v(self_->value.pluginNamespace());
        Meta::Value result = v[istring(name)];
        return PyMotorObject::stealValue(self, result);
    }
    else
    {
        s_library->m_PyErr_Format(
            *s_library->m_PyExc_Exception,
            minitl::format<>(FMT("while retrieving property {0}: plugin {1} failed to load"), name,
                             self_->value.name()));
        return nullptr;
    }
}

int PyMotorPlugin::setattr(PyObject* self, const char* name, PyObject* value)
{
    motor_forceuse(self);
    motor_forceuse(name);
    motor_forceuse(value);
    return 0;
}

PyObject* PyMotorPlugin::repr(PyObject* self)
{
    auto* self_ = reinterpret_cast< PyMotorPlugin* >(self);
    if(s_library->getVersion() >= 30)
    {
        return s_library->m_PyUnicode_FromString(
            minitl::format<>(FMT("[plugin {0}]"), self_->value.name()));
    }
    else
    {
        return s_library->m_PyString_FromString(
            minitl::format<>(FMT("[plugin {0}]"), self_->value.name()));
    }
}

void PyMotorPlugin::dealloc(PyObject* self)
{
    auto* self_ = reinterpret_cast< PyMotorPlugin* >(self);
    self_->value.~Plugin();
    self->py_type->tp_free(self);
}

void PyMotorPlugin::registerType(PyObject* module)
{
    int result = s_library->m_PyType_Ready(&s_motorPluginType);
    motor_assert(result >= 0, "unable to register type");
    Py_INCREF(&s_motorPluginType);
    result = (*s_library->m_PyModule_AddObject)(module, "Plugin", (PyObject*)&s_motorPluginType);
    motor_assert(result >= 0, "unable to register type");
    motor_forceuse(result);
}

}}  // namespace Motor::Python
