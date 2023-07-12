/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <stdafx.h>
#include <gvalue.hh>

#include <gobject/genums.h>
#include <gobject/gobject.h>
#include <gobject/gvaluetypes.h>
#include <gtkresourcedescription.meta.hh>

#include <motor/meta/operatortable.hh>
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
        raw< const Meta::OperatorTable::ConversionOperators< i64 > > signedIntegerOperators
            = value.type().metaclass->operators->signedIntegerOperators;
        raw< const Meta::OperatorTable::ConversionOperators< u64 > > unsignedIntegerOperators
            = value.type().metaclass->operators->unsignedIntegerOperators;
        if(signedIntegerOperators)
        {
            g_value_init(target, type);
            g_value_set_schar(target, (i8)(*signedIntegerOperators->get)(value));
            return true;
        }
        else if(unsignedIntegerOperators)
        {
            g_value_init(target, type);
            g_value_set_schar(target, (i8)(*unsignedIntegerOperators->get)(value));
            return true;
        }
        else
        {
            return false;
        }
    }
    case G_TYPE_UCHAR:
    {
        raw< const Meta::OperatorTable::ConversionOperators< i64 > > signedIntegerOperators
            = value.type().metaclass->operators->signedIntegerOperators;
        raw< const Meta::OperatorTable::ConversionOperators< u64 > > unsignedIntegerOperators
            = value.type().metaclass->operators->unsignedIntegerOperators;
        if(unsignedIntegerOperators)
        {
            g_value_init(target, type);
            g_value_set_uchar(target, (u8)(*unsignedIntegerOperators->get)(value));
            return true;
        }
        else if(signedIntegerOperators)
        {
            g_value_init(target, type);
            g_value_set_uchar(target, (u8)(*signedIntegerOperators->get)(value));
            return true;
        }
        else
        {
            return false;
        }
    }
    case G_TYPE_BOOLEAN:
    {
        raw< const Meta::OperatorTable::ConversionOperators< bool > > boolOperators
            = value.type().metaclass->operators->boolOperators;
        if(boolOperators)
        {
            g_value_init(target, type);
            g_value_set_boolean(target, (*boolOperators->get)(value));
            return true;
        }
        else
        {
            return false;
        }
    }
    case G_TYPE_INT:
    {
        raw< const Meta::OperatorTable::ConversionOperators< i64 > > signedIntegerOperators
            = value.type().metaclass->operators->signedIntegerOperators;
        raw< const Meta::OperatorTable::ConversionOperators< u64 > > unsignedIntegerOperators
            = value.type().metaclass->operators->unsignedIntegerOperators;
        if(signedIntegerOperators)
        {
            g_value_init(target, type);
            g_value_set_int(target, (i32)(*signedIntegerOperators->get)(value));
            return true;
        }
        else if(unsignedIntegerOperators)
        {
            g_value_init(target, type);
            g_value_set_int(target, (i32)(*unsignedIntegerOperators->get)(value));
            return true;
        }
        else
        {
            return false;
        }
    }
    case G_TYPE_UINT:
    {
        raw< const Meta::OperatorTable::ConversionOperators< i64 > > signedIntegerOperators
            = value.type().metaclass->operators->signedIntegerOperators;
        raw< const Meta::OperatorTable::ConversionOperators< u64 > > unsignedIntegerOperators
            = value.type().metaclass->operators->unsignedIntegerOperators;
        if(unsignedIntegerOperators)
        {
            g_value_init(target, type);
            g_value_set_uint(target, (u32)(*unsignedIntegerOperators->get)(value));
            return true;
        }
        else if(signedIntegerOperators)
        {
            g_value_init(target, type);
            g_value_set_uint(target, (u32)(*signedIntegerOperators->get)(value));
            return true;
        }
        else
        {
            return false;
        }
    }
    case G_TYPE_LONG:
    {
        raw< const Meta::OperatorTable::ConversionOperators< i64 > > signedIntegerOperators
            = value.type().metaclass->operators->signedIntegerOperators;
        raw< const Meta::OperatorTable::ConversionOperators< u64 > > unsignedIntegerOperators
            = value.type().metaclass->operators->unsignedIntegerOperators;
        if(signedIntegerOperators)
        {
            g_value_init(target, type);
            g_value_set_long(target, (glong)(*signedIntegerOperators->get)(value));
            return true;
        }
        else if(unsignedIntegerOperators)
        {
            g_value_init(target, type);
            g_value_set_long(target, (glong)(*unsignedIntegerOperators->get)(value));
            return true;
        }
        else
        {
            return false;
        }
    }
    case G_TYPE_INT64:
    {
        raw< const Meta::OperatorTable::ConversionOperators< i64 > > signedIntegerOperators
            = value.type().metaclass->operators->signedIntegerOperators;
        raw< const Meta::OperatorTable::ConversionOperators< u64 > > unsignedIntegerOperators
            = value.type().metaclass->operators->unsignedIntegerOperators;
        if(signedIntegerOperators)
        {
            g_value_init(target, type);
            g_value_set_int64(target, (i64)(*signedIntegerOperators->get)(value));
            return true;
        }
        else if(unsignedIntegerOperators)
        {
            g_value_init(target, type);
            g_value_set_int64(target, (i64)(*unsignedIntegerOperators->get)(value));
            return true;
        }
        else
        {
            return false;
        }
    }
    case G_TYPE_ULONG:
    {
        raw< const Meta::OperatorTable::ConversionOperators< i64 > > signedIntegerOperators
            = value.type().metaclass->operators->signedIntegerOperators;
        raw< const Meta::OperatorTable::ConversionOperators< u64 > > unsignedIntegerOperators
            = value.type().metaclass->operators->unsignedIntegerOperators;
        if(unsignedIntegerOperators)
        {
            g_value_init(target, type);
            g_value_set_ulong(target, (gulong)(*unsignedIntegerOperators->get)(value));
            return true;
        }
        else if(signedIntegerOperators)
        {
            g_value_init(target, type);
            g_value_set_ulong(target, (gulong)(*signedIntegerOperators->get)(value));
            return true;
        }
        else
        {
            return false;
        }
    }
    case G_TYPE_UINT64:
    {
        raw< const Meta::OperatorTable::ConversionOperators< i64 > > signedIntegerOperators
            = value.type().metaclass->operators->signedIntegerOperators;
        raw< const Meta::OperatorTable::ConversionOperators< u64 > > unsignedIntegerOperators
            = value.type().metaclass->operators->unsignedIntegerOperators;
        if(unsignedIntegerOperators)
        {
            g_value_init(target, type);
            g_value_set_uint64(target, (u64)(*unsignedIntegerOperators->get)(value));
            return true;
        }
        else if(signedIntegerOperators)
        {
            g_value_init(target, type);
            g_value_set_uint64(target, (u64)(*signedIntegerOperators->get)(value));
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
        raw< const Meta::OperatorTable::ConversionOperators< float > > floatOperators
            = value.type().metaclass->operators->floatOperators;
        raw< const Meta::OperatorTable::ConversionOperators< double > > doubleOperators
            = value.type().metaclass->operators->doubleOperators;
        if(floatOperators)
        {
            g_value_init(target, type);
            g_value_set_float(target, (float)(*floatOperators->get)(value));
            return true;
        }
        else if(doubleOperators)
        {
            g_value_init(target, type);
            g_value_set_float(target, (float)(*doubleOperators->get)(value));
            return true;
        }
        else
        {
            return false;
        }
    }
    case G_TYPE_DOUBLE:
    {
        raw< const Meta::OperatorTable::ConversionOperators< float > > floatOperators
            = value.type().metaclass->operators->floatOperators;
        raw< const Meta::OperatorTable::ConversionOperators< double > > doubleOperators
            = value.type().metaclass->operators->doubleOperators;
        if(doubleOperators)
        {
            g_value_init(target, type);
            g_value_set_double(target, (double)(*doubleOperators->get)(value));
            return true;
        }
        else if(floatOperators)
        {
            g_value_init(target, type);
            g_value_set_double(target, (double)(*floatOperators->get)(value));
            return true;
        }
        else
        {
            return false;
        }
    }
    case G_TYPE_STRING:
    {
        raw< const Meta::OperatorTable::ConversionOperators< const char* > > stringOperators
            = value.type().metaclass->operators->stringOperators;
        if(stringOperators)
        {
            g_value_init(target, type);
            g_value_set_string(target, (*stringOperators->get)(value));
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
