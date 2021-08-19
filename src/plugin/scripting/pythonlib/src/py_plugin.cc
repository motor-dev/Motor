/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <motor/plugin.scripting.pythonlib/stdafx.h>
#include <motor/plugin.scripting.pythonlib/pythonlib.hh>
#include <py_object.hh>
#include <py_plugin.hh>

namespace Motor { namespace Python {

static PyTypeObject s_motorPluginType = {{{0, 0}, 0},
                                         "py_motor.Plugin",
                                         sizeof(PyMotorPlugin),
                                         0,
                                         &PyMotorPlugin::dealloc,
                                         0,
                                         &PyMotorPlugin::getattr,
                                         &PyMotorPlugin::setattr,
                                         0,
                                         &PyMotorPlugin::repr,
                                         0,
                                         0,
                                         0,
                                         0,
                                         0,
                                         0,
                                         0,
                                         0,
                                         0,
                                         Py_TPFLAGS_DEFAULT,
                                         "Wrapper class for the C++ class Motor::Plugin::Plugin",
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
                                         0,
                                         0,
                                         &PyMotorPlugin::init,
                                         0,
                                         &PyMotorPlugin::create,
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

PyObject* PyMotorPlugin::create(PyTypeObject* type, PyObject* /*args*/, PyObject* /*kwds*/)
{
    PyMotorPlugin* self = reinterpret_cast< PyMotorPlugin* >(type->tp_alloc(type, 0));
    new(&self->value) Plugin::Plugin< void >();
    return reinterpret_cast< PyObject* >(self);
}

int PyMotorPlugin::init(PyObject* self, PyObject* args, PyObject* /*kwds*/)
{
    PyMotorPlugin* self_ = reinterpret_cast< PyMotorPlugin* >(self);
    const char*    name  = 0;
    if(s_library->m__PyArg_ParseTuple_SizeT(args, "s", &name))
    {
        self_->value = Plugin::Plugin< void >(name, Plugin::Plugin< void >::Preload);
        return 0;
    }
    else
    {
        return -1;
    }
}

PyObject* PyMotorPlugin::getattr(PyObject* self, const char* name)
{
    PyMotorPlugin* self_ = reinterpret_cast< PyMotorPlugin* >(self);
    if(self_->value)
    {
        Meta::Value v(self_->value.pluginNamespace());
        Meta::Value result = v[name];
        return PyMotorObject::stealValue(self, result);
    }
    else
    {
        s_library->m_PyErr_Format(*s_library->m_PyExc_Exception,
                                  "while retrieving property %s: plugin %s failed to load", name,
                                  self_->value.name().str().name);
        return 0;
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
    PyMotorPlugin* self_ = reinterpret_cast< PyMotorPlugin* >(self);
    if(s_library->getVersion() >= 30)
    {
        PyUnicode_FromFormatType f = s_library->m_PyUnicode_FromFormat;
        return f("[plugin %s]", self_->value.name().str().name);
    }
    else
    {
        return s_library->m_PyString_FromFormat("[plugin %s]", self_->value.name().str().name);
    }
}

void PyMotorPlugin::dealloc(PyObject* self)
{
    PyMotorPlugin* self_ = reinterpret_cast< PyMotorPlugin* >(self);
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
