/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <stdafx.h>
#include <gvalue.hh>

#include <gobject/genums.h>
#include <gobject/gobject.h>
#include <gobject/gvaluetypes.h>
#include <gtkresourcedescription.meta.hh>

#include <motor/meta/value.hh>
#include <motor/minitl/cast.hh>

namespace Motor { namespace Gtk3 {

template < typename T >
static T convertNumberToInteger(const Meta::Value& value)
{
    motor_assert(value.type().metaclass->type() == Meta::ClassType_Number,
                 "value is not of Number type");
    switch(value.type().metaclass->index())
    {
    case Meta::ClassIndex_bool:
    {
        return T(value.as< bool >());
    }
    case Meta::ClassIndex_u8:
    {
        return motor_checked_numcast< T >(value.as< u8 >());
    }
    case Meta::ClassIndex_u16:
    {
        return motor_checked_numcast< T >(value.as< u16 >());
    }
    case Meta::ClassIndex_u32:
    {
        return motor_checked_numcast< T >(value.as< u32 >());
    }
    case Meta::ClassIndex_u64:
    {
        return motor_checked_numcast< T >(value.as< u64 >());
    }
    case Meta::ClassIndex_i8:
    {
        return motor_checked_numcast< T >(value.as< i8 >());
    }
    case Meta::ClassIndex_i16:
    {
        return motor_checked_numcast< T >(value.as< i16 >());
    }
    case Meta::ClassIndex_i32:
    {
        return motor_checked_numcast< T >(value.as< i32 >());
    }
    case Meta::ClassIndex_i64:
    {
        return motor_checked_numcast< T >(value.as< i64 >());
    }
    case Meta::ClassIndex_float:
    {
        return T(value.as< float >());
    }
    case Meta::ClassIndex_double:
    {
        return T(value.as< double >());
    }
    default: motor_notreached(); return T();
    }
}

bool convertMetaValueToGValue(const Meta::Value& value, GType type, GValue* target)
{
    if(G_TYPE_FUNDAMENTAL(type) == G_TYPE_GTYPE)
    {
        motor_assert(false, "don't know how to handle type %s" | g_type_name(type));
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
        g_value_init(target, type);
        g_value_set_uchar(target, convertNumberToInteger< i8 >(value));
        return true;
    }
    case G_TYPE_UCHAR:
    {
        g_value_init(target, type);
        g_value_set_uchar(target, convertNumberToInteger< u8 >(value));
        return true;
    }
    case G_TYPE_BOOLEAN:
    {
        g_value_init(target, type);
        g_value_set_boolean(target, convertNumberToInteger< bool >(value));
        return true;
    }
    case G_TYPE_INT:
    {
        g_value_init(target, type);
        g_value_set_int(target, convertNumberToInteger< i32 >(value));
        return true;
    }
    case G_TYPE_UINT:
    {
        g_value_init(target, type);
        g_value_set_uint(target, convertNumberToInteger< u32 >(value));
        return true;
    }
    case G_TYPE_LONG:
    {
        g_value_init(target, type);
        g_value_set_long(target, convertNumberToInteger< long >(value));
        return true;
    }
    case G_TYPE_INT64:
    {
        g_value_init(target, type);
        g_value_set_int64(target, convertNumberToInteger< i64 >(value));
        return true;
    }
    case G_TYPE_ULONG:
    {
        g_value_init(target, type);
        g_value_set_ulong(target, convertNumberToInteger< unsigned long >(value));
        return true;
    }
    case G_TYPE_UINT64:
    {
        g_value_init(target, type);
        g_value_set_uint64(target, convertNumberToInteger< u64 >(value));
        return true;
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
        g_value_init(target, type);
        g_value_set_float(target, convertNumberToInteger< float >(value));
        return true;
    }
    case G_TYPE_DOUBLE:
    {
        g_value_init(target, type);
        g_value_set_double(target, convertNumberToInteger< double >(value));
        return true;
    }
    case G_TYPE_STRING:
    {
        motor_assert(value.type().metaclass->type() == Meta::ClassType_String,
                     "value is not of String type");
        switch(value.type().metaclass->index())
        {
        case Meta::ClassIndex_istring:
        {
            g_value_init(target, type);
#ifdef GLIB_VERSION_2_66
            g_value_set_interned_string(target, value.as< const istring& >().c_str());
#else
            g_value_set_static_string(target, value.as< const istring& >().c_str());
#endif
            return true;
        }
        case Meta::ClassIndex_inamespace:
        {
            inamespace::Path f = value.as< const inamespace& >().str();
            g_value_init(target, type);
            g_value_set_string(target, f);
            return true;
        }
        case Meta::ClassIndex_ifilename:
        {
            ifilename::Filename f = value.as< const ifilename& >().str();
            g_value_init(target, type);
            g_value_set_string(target, f);
            return true;
        }
        case Meta::ClassIndex_ipath:
        {
            ipath::Filename f = value.as< const ipath& >().str();
            g_value_init(target, type);
            g_value_set_string(target, f);
            return true;
        }
        case Meta::ClassIndex_text:
        {
            const char* t = value.as< const text& >().begin();
            if(t)
            {
                g_value_init(target, type);
                g_value_set_string(target, t);
                return true;
            }
            else
            {
                return false;
            }
        }
        default: motor_notreached(); return false;
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
        motor_assert(false, "don't know how to handle type %s" | g_type_name(type));
        return false;
    }
    }
}

}}  // namespace Motor::Gtk3
