/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#ifndef MOTOR_GUI_GTK3_GTK3PLUGIN_HH_
#define MOTOR_GUI_GTK3_GTK3PLUGIN_HH_
/**************************************************************************************************/
#include <motor/core/memory/allocators/system.hh>
#include <glib-object.h>

namespace Motor { namespace Gtk3 {

class Gtk3Plugin
{
private:
    struct Page;

private:
    SystemAllocator               m_allocator;
    Page*                         m_firstPage;
    GQuark                        m_motorQuark;
    raw< const Meta::ObjectInfo > m_objectPtr;

private:
    void* allocate(u32 size);
    void  registerType(GType type, raw< const Meta::Class > parent);
    void  registerTypeContent(GType type);
    void  unregisterType(GType type);

public:
    Gtk3Plugin();
    ~Gtk3Plugin();

    template < typename T >
    T* allocate()
    {
        return static_cast< T* >(allocate(sizeof(T)));
    }
};

}}  // namespace Motor::Gtk3

/**************************************************************************************************/
#endif
