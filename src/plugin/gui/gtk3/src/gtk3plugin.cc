/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <stdafx.h>

#include <gtk3plugin.hh>

#include <gboxed.hh>
#include <genum.hh>
#include <gflags.hh>
#include <ginterface.hh>
#include <gobject.hh>
#include <gtkresourcedescription.meta.hh>

#include <motor/meta/engine/helper/method.hh>
#include <motor/meta/engine/methodinfo.meta.hh>
#include <motor/meta/engine/namespace.hh>
#include <motor/plugin/plugin.hh>

#include <meta/constructor.meta.hh>
#include <meta/property.meta.hh>

#include <gobject/gvaluetypes.h>

namespace Motor {

raw< Meta::Class > motor_plugin_gui_gtk3_Namespace();

}

namespace Motor { namespace Gtk3 {

static void log(const gchar* domain, GLogLevelFlags log_level, const gchar* message,
                gpointer userData)
{
    weak< Logger >& logger = *reinterpret_cast< weak< Logger >* >(userData);
    LogLevel        level  = logInfo;
    switch(log_level & G_LOG_LEVEL_MASK)
    {
    case G_LOG_LEVEL_ERROR: level = logFatal; break;
    case G_LOG_LEVEL_CRITICAL: level = logError; break;
    case G_LOG_LEVEL_WARNING: level = logWarning; break;
    case G_LOG_LEVEL_MESSAGE:
    case G_LOG_LEVEL_INFO: level = logInfo; break;
    case G_LOG_LEVEL_DEBUG: level = logDebug; break;
    }
    if(domain)
        logger->getChild(domain)->log(level, "", 0, message);
    else
        logger->log(level, "", 0, message);
}

struct Gtk3Plugin::Page
{
    Page* next;
    u8*   current;
    u8    memory[64 * 1024 - sizeof(Page*) - sizeof(u8*)];
};

Gtk3Plugin::Gtk3Plugin()
    : m_allocator(SystemAllocator::BlockSize_64k, 1)
    , m_firstPage(static_cast< Page* >(m_allocator.allocate()))
    , m_motorQuark(g_quark_from_static_string("motor"))
    , m_objectPtr(motor_plugin_gui_gtk3_Namespace()->objects)
    , m_logger(Log::gtk())
    , m_logHandlerDefault(g_log_set_handler(nullptr, GLogLevelFlags(~0), log, &m_logger))
    , m_logHandlerGLib(g_log_set_handler("GLib", GLogLevelFlags(~0), log, &m_logger))
    , m_logHandlerGtk(g_log_set_handler("GTK", GLogLevelFlags(~0), log, &m_logger))
{
    g_log_set_default_handler(log, &m_logger);
    gtk_init(nullptr, nullptr);
    gtk_test_register_all_types();

    m_firstPage->next    = nullptr;
    m_firstPage->current = m_firstPage->memory;

    registerBoxed(G_TYPE_BOXED);
    registerEnum(G_TYPE_ENUM);
    registerFlags(G_TYPE_FLAGS);
    registerInterface(G_TYPE_INTERFACE);
    registerClass(G_TYPE_OBJECT);
}

Gtk3Plugin::~Gtk3Plugin()
{
    motor_plugin_gui_gtk3_Namespace()->objects = m_objectPtr;
    unregisterClass(G_TYPE_OBJECT);
    unregisterInterface(G_TYPE_INTERFACE);

    g_log_set_default_handler(nullptr, nullptr);
    while(m_firstPage)
    {
        Page* next = m_firstPage->next;
        m_allocator.free(m_firstPage);
        m_firstPage = next;
    }
    g_log_remove_handler("Gtk", m_logHandlerGtk);
    g_log_remove_handler("GLib", m_logHandlerGLib);
    g_log_remove_handler(nullptr, m_logHandlerDefault);
}

void* Gtk3Plugin::allocate(u32 size)
{
    if(m_firstPage->current + size > m_firstPage->memory + sizeof(m_firstPage->memory))
    {
        Page* page    = static_cast< Page* >(m_allocator.allocate());
        page->next    = m_firstPage;
        page->current = page->memory;
        m_firstPage   = page;
    }
    void* result = m_firstPage->current;
    m_firstPage->current += size;
    return result;
}

void Gtk3Plugin::registerValue(const istring& name, const Meta::Value& value)
{
    Meta::ObjectInfo objectTemplate
        = {motor_plugin_gui_gtk3_Namespace()->objects, {nullptr}, name, Meta::Value()};
    void* memory  = this->allocate< Meta::ObjectInfo >();
    auto* object  = new(memory) Meta::ObjectInfo(objectTemplate);
    object->value = value;

    motor_plugin_gui_gtk3_Namespace()->objects.set(object);
}

void Gtk3Plugin::registerBoxed(GType type)
{
    getGBoxedClass(*this, type);

    guint  childrenCount;
    GType* children = g_type_children(type, &childrenCount);
    for(guint i = 0; i < childrenCount; ++i)
    {
        registerBoxed(children[i]);
    }
    g_free(children);
}

void Gtk3Plugin::registerEnum(GType type)
{
    getGEnumClass(*this, type);

    guint  childrenCount;
    GType* children = g_type_children(type, &childrenCount);
    for(guint i = 0; i < childrenCount; ++i)
    {
        registerEnum(children[i]);
    }
    g_free(children);
}

void Gtk3Plugin::registerFlags(GType type)
{
    getGFlagsClass(*this, type);

    guint  childrenCount;
    GType* children = g_type_children(type, &childrenCount);
    for(guint i = 0; i < childrenCount; ++i)
    {
        registerFlags(children[i]);
    }
    g_free(children);
}

void Gtk3Plugin::registerInterface(GType type)
{
    getGInterfaceClass(*this, type);

    guint  childrenCount;
    GType* children = g_type_children(type, &childrenCount);
    for(guint i = 0; i < childrenCount; ++i)
    {
        registerInterface(children[i]);
    }
    g_free(children);
}

void Gtk3Plugin::unregisterInterface(GType type)
{
    destroyGInterfaceClass(*this, type);
    guint  childrenCount;
    GType* children = g_type_children(type, &childrenCount);
    for(guint i = 0; i < childrenCount; ++i)
    {
        unregisterInterface(children[i]);
    }
    g_free(children);
    g_type_set_qdata(type, m_motorQuark, nullptr);
}

void Gtk3Plugin::registerClass(GType type)
{
    getGObjectClass(*this, type);

    guint  childrenCount;
    GType* children = g_type_children(type, &childrenCount);
    for(guint i = 0; i < childrenCount; ++i)
    {
        registerClass(children[i]);
    }
    g_free(children);
}

void Gtk3Plugin::unregisterClass(GType type)
{
    destroyGObjectClass(*this, type);
    guint  childrenCount;
    GType* children = g_type_children(type, &childrenCount);
    for(guint i = 0; i < childrenCount; ++i)
    {
        unregisterClass(children[i]);
    }
    g_free(children);
    g_type_set_qdata(type, m_motorQuark, nullptr);
}

Meta::Type Gtk3Plugin::fromGType(GType type)
{
    motor_forceuse(this);
    if(G_TYPE_FUNDAMENTAL(type) == G_TYPE_GTYPE)
    {
        return motor_type< raw< const Meta::Class > >();
    }

    switch(G_TYPE_FUNDAMENTAL(type))
    {
    case G_TYPE_NONE: return motor_type< void >();
    case G_TYPE_INTERFACE:
    {
        raw< const Meta::Class > cls = getGInterfaceClass(*this, type);
        return Meta::Type::makeType(cls, Meta::Type::Indirection::Value,
                                    Meta::Type::Constness::Mutable, Meta::Type::Constness::Mutable);
    }
    case G_TYPE_CHAR: return motor_type< i8 >();
    case G_TYPE_UCHAR: return motor_type< u8 >();
    case G_TYPE_BOOLEAN: return motor_type< bool >();
    case G_TYPE_INT: return motor_type< i32 >();
    case G_TYPE_UINT: return motor_type< u32 >();
    case G_TYPE_LONG: return motor_type< i64 >();
    case G_TYPE_ULONG: return motor_type< u64 >();
    case G_TYPE_INT64: return motor_type< i64 >();
    case G_TYPE_UINT64: return motor_type< u64 >();
    case G_TYPE_ENUM:
    {
        raw< const Meta::Class > cls = getGEnumClass(*this, type);
        return Meta::Type::makeType(cls, Meta::Type::Indirection::Value,
                                    Meta::Type::Constness::Mutable, Meta::Type::Constness::Mutable);
    }
    case G_TYPE_FLAGS:
    {
        raw< const Meta::Class > cls = getGFlagsClass(*this, type);
        return Meta::Type::makeType(cls, Meta::Type::Indirection::Value,
                                    Meta::Type::Constness::Mutable, Meta::Type::Constness::Mutable);
    }
    case G_TYPE_FLOAT: return motor_type< float >();
    case G_TYPE_DOUBLE: return motor_type< double >();
    case G_TYPE_STRING: return motor_type< text >();
    case G_TYPE_BOXED:
    {
        raw< const Meta::Class > cls = getGBoxedClass(*this, type);
        return Meta::Type::makeType(cls, Meta::Type::Indirection::Value,
                                    Meta::Type::Constness::Mutable, Meta::Type::Constness::Mutable);
    }
    case G_TYPE_OBJECT:
    {
        raw< const Meta::Class > cls = getGObjectClass(*this, type);
        return Meta::Type::makeType(cls, Meta::Type::Indirection::Value,
                                    Meta::Type::Constness::Mutable, Meta::Type::Constness::Mutable);
    }
    case G_TYPE_VARIANT: return motor_type< Meta::Value >();
    case G_TYPE_PARAM:
    case G_TYPE_POINTER:
    default:
    {
        motor_assert_format(false, "don't know how to handle type {0}", g_type_name(type));
        return motor_type< void >();
    }
    }
}

Meta::Value Gtk3Plugin::fromGValue(const GValue* value)
{
    motor_forceuse(this);
    motor_assert(value != nullptr, "NULL value");
    GType type = G_VALUE_TYPE(value);
    if(G_TYPE_FUNDAMENTAL(type) == G_TYPE_GTYPE)
    {
        motor_assert_format(false, "don't know how to handle type {0}", g_type_name(type));
        return {};
    }

    switch(G_TYPE_FUNDAMENTAL(type))
    {
    case G_TYPE_NONE: return {};
    case G_TYPE_INTERFACE:
    {
        raw< const Meta::Class > cls    = getGInterfaceClass(*this, type);
        GObjectWrapper           object = {reinterpret_cast< GObject* >(g_value_get_object(value))};

        return {Meta::Type::makeType(cls, Meta::Type::Indirection::Value,
                                     Meta::Type::Constness::Mutable,
                                     Meta::Type::Constness::Mutable),
                &object, Meta::Value::MakeCopy};
    }
    case G_TYPE_CHAR: return Meta::Value(g_value_get_schar(value));
    case G_TYPE_UCHAR: return Meta::Value(g_value_get_uchar(value));
    case G_TYPE_BOOLEAN: return Meta::Value(g_value_get_boolean(value) ? true : false);
    case G_TYPE_INT: return Meta::Value(i32(g_value_get_int(value)));
    case G_TYPE_UINT: return Meta::Value(u32(g_value_get_uint(value)));
    case G_TYPE_LONG: return Meta::Value(i64(g_value_get_long(value)));
    case G_TYPE_ULONG: return Meta::Value(u64(g_value_get_ulong(value)));
    case G_TYPE_INT64: return Meta::Value(i64(g_value_get_int64(value)));
    case G_TYPE_UINT64: return Meta::Value(u64(g_value_get_uint64(value)));
    case G_TYPE_ENUM:
    {
        raw< const Meta::Class > cls       = getGEnumClass(*this, type);
        GEnumWrapper             enumValue = {g_value_get_enum(value)};
        return {Meta::Type::makeType(cls, Meta::Type::Indirection::Value,
                                     Meta::Type::Constness::Mutable,
                                     Meta::Type::Constness::Mutable),
                &enumValue, Meta::Value::MakeCopy};
    }
    case G_TYPE_FLAGS:
    {
        raw< const Meta::Class > cls        = getGFlagsClass(*this, type);
        GFlagsWrapper            flagsValue = {g_value_get_flags(value)};
        return {Meta::Type::makeType(cls, Meta::Type::Indirection::Value,
                                     Meta::Type::Constness::Mutable,
                                     Meta::Type::Constness::Mutable),
                &flagsValue, Meta::Value::MakeCopy};
    }
    case G_TYPE_FLOAT: return Meta::Value(g_value_get_float(value));
    case G_TYPE_DOUBLE: return Meta::Value(g_value_get_double(value));
    case G_TYPE_STRING: return Meta::Value(text(g_value_get_string(value)));
    case G_TYPE_BOXED:
    {
        // raw< const Meta::Class > cls = getGBoxedClass(*this, type);
        raw< const Meta::Class > cls        = getGBoxedClass(*this, type);
        GBoxedWrapper            boxedValue = {g_value_get_boxed(value)};
        return {Meta::Type::makeType(cls, Meta::Type::Indirection::Value,
                                     Meta::Type::Constness::Mutable,
                                     Meta::Type::Constness::Mutable),
                &boxedValue, Meta::Value::MakeCopy};
    }
    case G_TYPE_OBJECT:
    {
        raw< const Meta::Class > cls    = getGObjectClass(*this, type);
        GObjectWrapper           object = {reinterpret_cast< GObject* >(g_value_get_object(value))};
        return {Meta::Type::makeType(cls, Meta::Type::Indirection::Value,
                                     Meta::Type::Constness::Mutable,
                                     Meta::Type::Constness::Mutable),
                &object, Meta::Value::MakeCopy};
    }
    case G_TYPE_VARIANT:
    case G_TYPE_PARAM:
    case G_TYPE_POINTER:
    default:
    {
        motor_assert_format(false, "don't know how to handle type {0}", g_type_name(type));
        return {};
    }
    }
}

MOTOR_EXPORT Gtk3Plugin s_gtk3Plugin;

}}  // namespace Motor::Gtk3
