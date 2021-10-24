/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <stdafx.h>
#include <gobject.hh>

#include <gtkresourcedescription.meta.hh>
#include <gvalue.hh>
#include <meta/constructor.meta.hh>

#include <motor/meta/value.hh>

namespace Motor { namespace Gtk3 {

Meta::Value Constructor::call(raw< const Meta::Method > method, Meta::Value* params, u32 nparams)
{
    motor_forceuse(method);
    const char** names  = static_cast< const char** >(malloca(nparams * sizeof(char*)));
    GValue*      values = static_cast< GValue* >(malloca(nparams * sizeof(GValue)));

    raw< const Constructor > constructor
        = {reinterpret_cast< const Constructor* >(method.operator->())};
    GType         type        = constructor->type;
    GObjectClass* objectClass = static_cast< GObjectClass* >(g_type_class_ref(type));
    guint         paramSpecCount;
    GParamSpec**  paramSpecs = g_object_class_list_properties(objectClass, &paramSpecCount);

    u32 actualParamCount = 0;

    for(guint i = 0, j = 0; i < paramSpecCount; ++i)
    {
        if(paramSpecs[i]->value_type == G_TYPE_POINTER
           || paramSpecs[i]->value_type == G_TYPE_VARIANT
           || paramSpecs[i]->flags & G_PARAM_DEPRECATED)
        {
            continue;
        }
        if(((paramSpecs[i]->flags & G_PARAM_READWRITE) == G_PARAM_READWRITE)
           || (paramSpecs[i]->flags & G_PARAM_CONSTRUCT))
        {
            motor_assert(actualParamCount < nparams, "invalid parameter count");
            values[actualParamCount] = G_VALUE_INIT;
            if(convertMetaValueToGValue(params[j], paramSpecs[i]->value_type,
                                        &values[actualParamCount]))
            {
                names[actualParamCount] = g_param_spec_get_name(paramSpecs[i]);
                ++actualParamCount;
            }
            ++j;
        }
    }

    GObjectWrapper object = {g_object_new_with_properties(type, actualParamCount, names, values)};
    motor_assert(method->overloads.count == 1,
                 "Constructor for type %s has more than one overload" | g_type_name(type));
    Meta::Type  returnType = method->overloads[0].returnType;
    Meta::Value result(returnType, &object, Meta::Value::MakeCopy);
    g_type_class_unref(objectClass);

    for(guint i = 0; i < actualParamCount; ++i)
    {
        g_value_unset(&values[actualParamCount - i - 1]);
    }

    freea(values);
    freea(names);

    return result;
}

}}  // namespace Motor::Gtk3
