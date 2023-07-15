/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <stdafx.h>
#include <gvalue.hh>

#include <gobject/genums.h>
#include <gobject/gobject.h>
#include <gobject/gvaluetypes.h>
#include <gtkresourcedescription.meta.hh>

#include <motor/meta/interfacetable.hh>
#include <motor/meta/value.hh>
#include <motor/minitl/cast.hh>

namespace Motor { namespace Gtk3 {

bool convertMetaValueToGValue(const Meta::Value& value, GType type, GValue* target)
{
    if(G_TYPE_FUNDAMENTAL(type) == G_TYPE_GTYPE)
    {
        motor_assert_format(false, "don't know how to handle type {0}", g_type_name(type));
        return false;
    }

    switch(G_TYPE_FUNDAMENTAL(type))
    {
    case G_TYPE_NONE: return false;
    case G_TYPE_INTERFACE:
    case G_TYPE_OBJECT:
    {
        GObject* object = value.as< const GObjectWrapper& >().value;
        if(object)
        {
            g_value_init(target, type);
            g_value_set_object(target, object);
            return true;
        }
        else
        {
            return false;
        }
    }
    case G_TYPE_CHAR:
    {
        raw< const Meta::InterfaceTable::TypeInterface< i64 > > i64Interface
            = value.type().metaclass->interfaces->i64Interface;
        raw< const Meta::InterfaceTable::TypeInterface< u64 > > u64Interface
            = value.type().metaclass->interfaces->u64Interface;
        if(i64Interface)
        {
            g_value_init(target, type);
            g_value_set_schar(target, (i8)(*i64Interface->get)(value));
            return true;
        }
        else if(u64Interface)
        {
            g_value_init(target, type);
            g_value_set_schar(target, (i8)(*u64Interface->get)(value));
            return true;
        }
        else
        {
            return false;
        }
    }
    case G_TYPE_UCHAR:
    {
        raw< const Meta::InterfaceTable::TypeInterface< i64 > > i64Interface
            = value.type().metaclass->interfaces->i64Interface;
        raw< const Meta::InterfaceTable::TypeInterface< u64 > > u64Interface
            = value.type().metaclass->interfaces->u64Interface;
        if(u64Interface)
        {
            g_value_init(target, type);
            g_value_set_uchar(target, (u8)(*u64Interface->get)(value));
            return true;
        }
        else if(i64Interface)
        {
            g_value_init(target, type);
            g_value_set_uchar(target, (u8)(*i64Interface->get)(value));
            return true;
        }
        else
        {
            return false;
        }
    }
    case G_TYPE_BOOLEAN:
    {
        raw< const Meta::InterfaceTable::TypeInterface< bool > > boolInterface
            = value.type().metaclass->interfaces->boolInterface;
        if(boolInterface)
        {
            g_value_init(target, type);
            g_value_set_boolean(target, (*boolInterface->get)(value));
            return true;
        }
        else
        {
            return false;
        }
    }
    case G_TYPE_INT:
    {
        raw< const Meta::InterfaceTable::TypeInterface< i64 > > i64Interface
            = value.type().metaclass->interfaces->i64Interface;
        raw< const Meta::InterfaceTable::TypeInterface< u64 > > u64Interface
            = value.type().metaclass->interfaces->u64Interface;
        if(i64Interface)
        {
            g_value_init(target, type);
            g_value_set_int(target, (i32)(*i64Interface->get)(value));
            return true;
        }
        else if(u64Interface)
        {
            g_value_init(target, type);
            g_value_set_int(target, (i32)(*u64Interface->get)(value));
            return true;
        }
        else
        {
            return false;
        }
    }
    case G_TYPE_UINT:
    {
        raw< const Meta::InterfaceTable::TypeInterface< i64 > > i64Interface
            = value.type().metaclass->interfaces->i64Interface;
        raw< const Meta::InterfaceTable::TypeInterface< u64 > > u64Interface
            = value.type().metaclass->interfaces->u64Interface;
        if(u64Interface)
        {
            g_value_init(target, type);
            g_value_set_uint(target, (u32)(*u64Interface->get)(value));
            return true;
        }
        else if(i64Interface)
        {
            g_value_init(target, type);
            g_value_set_uint(target, (u32)(*i64Interface->get)(value));
            return true;
        }
        else
        {
            return false;
        }
    }
    case G_TYPE_LONG:
    {
        raw< const Meta::InterfaceTable::TypeInterface< i64 > > i64Interface
            = value.type().metaclass->interfaces->i64Interface;
        raw< const Meta::InterfaceTable::TypeInterface< u64 > > u64Interface
            = value.type().metaclass->interfaces->u64Interface;
        if(i64Interface)
        {
            g_value_init(target, type);
            g_value_set_long(target, (glong)(*i64Interface->get)(value));
            return true;
        }
        else if(u64Interface)
        {
            g_value_init(target, type);
            g_value_set_long(target, (glong)(*u64Interface->get)(value));
            return true;
        }
        else
        {
            return false;
        }
    }
    case G_TYPE_INT64:
    {
        raw< const Meta::InterfaceTable::TypeInterface< i64 > > i64Interface
            = value.type().metaclass->interfaces->i64Interface;
        raw< const Meta::InterfaceTable::TypeInterface< u64 > > u64Interface
            = value.type().metaclass->interfaces->u64Interface;
        if(i64Interface)
        {
            g_value_init(target, type);
            g_value_set_int64(target, (i64)(*i64Interface->get)(value));
            return true;
        }
        else if(u64Interface)
        {
            g_value_init(target, type);
            g_value_set_int64(target, (i64)(*u64Interface->get)(value));
            return true;
        }
        else
        {
            return false;
        }
    }
    case G_TYPE_ULONG:
    {
        raw< const Meta::InterfaceTable::TypeInterface< i64 > > i64Interface
            = value.type().metaclass->interfaces->i64Interface;
        raw< const Meta::InterfaceTable::TypeInterface< u64 > > u64Interface
            = value.type().metaclass->interfaces->u64Interface;
        if(u64Interface)
        {
            g_value_init(target, type);
            g_value_set_ulong(target, (gulong)(*u64Interface->get)(value));
            return true;
        }
        else if(i64Interface)
        {
            g_value_init(target, type);
            g_value_set_ulong(target, (gulong)(*i64Interface->get)(value));
            return true;
        }
        else
        {
            return false;
        }
    }
    case G_TYPE_UINT64:
    {
        raw< const Meta::InterfaceTable::TypeInterface< i64 > > i64Interface
            = value.type().metaclass->interfaces->i64Interface;
        raw< const Meta::InterfaceTable::TypeInterface< u64 > > u64Interface
            = value.type().metaclass->interfaces->u64Interface;
        if(u64Interface)
        {
            g_value_init(target, type);
            g_value_set_uint64(target, (u64)(*u64Interface->get)(value));
            return true;
        }
        else if(i64Interface)
        {
            g_value_init(target, type);
            g_value_set_uint64(target, (u64)(*i64Interface->get)(value));
            return true;
        }
        else
        {
            return false;
        }
    }
    case G_TYPE_ENUM:
    {
        gint enumValue = value.as< const GEnumWrapper >().value;
        if(enumValue)
        {
            g_value_init(target, type);
            g_value_set_enum(target, enumValue);
            return true;
        }
        else
        {
            return false;
        }
    }
    case G_TYPE_FLAGS:
    {
        guint flagsValue = value.as< const GFlagsWrapper >().value;
        if(flagsValue)
        {
            g_value_init(target, type);
            g_value_set_flags(target, flagsValue);
            return true;
        }
        else
        {
            return false;
        }
    }
    case G_TYPE_FLOAT:
    {
        raw< const Meta::InterfaceTable::TypeInterface< float > > floatInterface
            = value.type().metaclass->interfaces->floatInterface;
        raw< const Meta::InterfaceTable::TypeInterface< double > > doubleInterface
            = value.type().metaclass->interfaces->doubleInterface;
        if(floatInterface)
        {
            g_value_init(target, type);
            g_value_set_float(target, (float)(*floatInterface->get)(value));
            return true;
        }
        else if(doubleInterface)
        {
            g_value_init(target, type);
            g_value_set_float(target, (float)(*doubleInterface->get)(value));
            return true;
        }
        else
        {
            return false;
        }
    }
    case G_TYPE_DOUBLE:
    {
        raw< const Meta::InterfaceTable::TypeInterface< float > > floatInterface
            = value.type().metaclass->interfaces->floatInterface;
        raw< const Meta::InterfaceTable::TypeInterface< double > > doubleInterface
            = value.type().metaclass->interfaces->doubleInterface;
        if(doubleInterface)
        {
            g_value_init(target, type);
            g_value_set_double(target, (double)(*doubleInterface->get)(value));
            return true;
        }
        else if(floatInterface)
        {
            g_value_init(target, type);
            g_value_set_double(target, (double)(*floatInterface->get)(value));
            return true;
        }
        else
        {
            return false;
        }
    }
    case G_TYPE_STRING:
    {
        raw< const Meta::InterfaceTable::TypeInterface< const char* > > charpInterface
            = value.type().metaclass->interfaces->charpInterface;
        if(charpInterface)
        {
            g_value_init(target, type);
            g_value_set_string(target, (*charpInterface->get)(value));
            return true;
        }
        else
        {
            return false;
        }
    }
    case G_TYPE_BOXED:
    {
        gpointer boxed = value.as< const GBoxedWrapper& >().value;
        if(boxed)
        {
            g_value_init(target, type);
            g_value_set_boxed(target, boxed);
            return true;
        }
        else
        {
            return false;
        }
    }
    case G_TYPE_VARIANT:
    case G_TYPE_PARAM:
    case G_TYPE_POINTER:
    default:
    {
        motor_assert_format(false, "don't know how to handle type {0}", g_type_name(type));
        return false;
    }
    }
}

}}  // namespace Motor::Gtk3
