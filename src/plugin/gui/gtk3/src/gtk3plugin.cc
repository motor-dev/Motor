/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <stdafx.h>

#include <gtk3plugin.hh>

#include <gobject.hh>
#include <gtk3loader.hh>

#include <motor/meta/engine/helper/method.hh>
#include <motor/meta/engine/methodinfo.meta.hh>
#include <motor/meta/engine/namespace.hh>
#include <motor/plugin/plugin.hh>

namespace Motor { namespace Gtk3 {

struct Gtk3Plugin::Page
{
    Page* next;
    u32   current;
    u8    memory[64 * 1024 - sizeof(Page*) - sizeof(u8*)];
};

Gtk3Plugin::Gtk3Plugin()
    : m_allocator(SystemAllocator::BlockSize_64k, 1)
    , m_firstPage(static_cast< Page* >(m_allocator.allocate()))
    , m_motorQuark(g_quark_from_static_string("motor"))
{
    gtk_init(0, 0);
    gtk_test_register_all_types();

    m_firstPage->next    = 0;
    m_firstPage->current = 0;
}

Gtk3Plugin::~Gtk3Plugin()
{
}

}}  // namespace Motor::Gtk3

MOTOR_PLUGIN_REGISTER(Motor::Gtk3::Gtk3Loader);
