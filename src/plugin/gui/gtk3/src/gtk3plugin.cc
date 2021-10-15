/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <stdafx.h>

#include <gtk3plugin.hh>

#include <genericobject.meta.hh>
#include <gtk3loader.hh>

#include <motor/meta/engine/helper/method.hh>
#include <motor/meta/engine/methodinfo.meta.hh>
#include <motor/meta/engine/namespace.hh>
#include <motor/plugin/plugin.hh>

namespace Motor { namespace Gtk3 {

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
{
    gtk_init(0, 0);
    gtk_test_register_all_types();

    m_firstPage->next    = 0;
    m_firstPage->current = m_firstPage->memory;

    registerType(G_TYPE_OBJECT, motor_class< GenericObject >());
}

Gtk3Plugin::~Gtk3Plugin()
{
    motor_plugin_gui_gtk3_Namespace()->objects = m_objectPtr;
    unregisterType(G_TYPE_OBJECT);

    while(m_firstPage)
    {
        Page* next = m_firstPage->next;
        m_allocator.free(m_firstPage);
        m_firstPage = next;
    }
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

void Gtk3Plugin::registerType(GType type, raw< const Meta::Class > parent)
{
    Meta::Class* cls = new(allocate< Meta::Class >()) Meta::Class {istring(g_type_name(type)),
                                                                   sizeof(GenericObject),
                                                                   0,
                                                                   Meta::ClassType_Object,
                                                                   {0},
                                                                   parent,
                                                                   {0},
                                                                   {0},
                                                                   {0, 0},
                                                                   {0, 0},
                                                                   {0},
                                                                   {0},
                                                                   0,
                                                                   0};
    motor_info("registering GObject class %s" | cls->name);
    g_type_set_qdata(type, m_motorQuark, cls);
    raw< const Meta::Class > classPtr {cls};
    Meta::ObjectInfo*        object = new(allocate< Meta::ObjectInfo >())
        Meta::ObjectInfo {motor_plugin_gui_gtk3_Namespace()->objects,
                          {0},
                          cls->name,
                          Meta::Value(classPtr)};
    motor_plugin_gui_gtk3_Namespace()->objects.set(object);

    guint  childrenCount;
    GType* parents = g_type_children(type, &childrenCount);
    for(guint i = 0; i < childrenCount; ++i)
    {
        registerType(parents[i], classPtr);
    }
    g_free(parents);
}

void Gtk3Plugin::registerTypeContent(GType type)
{
    Meta::Class* cls = static_cast< Meta::Class* >(g_type_get_qdata(type, m_motorQuark));
    cls->constructor.set(0);

    guint  childrenCount;
    GType* parents = g_type_children(type, &childrenCount);
    for(guint i = 0; i < childrenCount; ++i)
    {
        registerTypeContent(parents[i]);
    }
    g_free(parents);
}

void Gtk3Plugin::unregisterType(GType type)
{
    g_type_set_qdata(type, m_motorQuark, 0);
    guint  childrenCount;
    GType* parents = g_type_children(type, &childrenCount);
    for(guint i = 0; i < childrenCount; ++i)
    {
        unregisterType(parents[i]);
    }
    g_free(parents);
}

static MOTOR_EXPORT Gtk3Plugin s_gtk3Plugin;

}}  // namespace Motor::Gtk3

MOTOR_PLUGIN_REGISTER(Motor::Gtk3::Gtk3Loader);
