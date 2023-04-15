/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <motor/plugin.graphics.windowing/stdafx.h>
#include <motor/core/threads/event.hh>
#include <motor/plugin.graphics.windowing/renderer.hh>
#include <motor/plugin.graphics.windowing/window.hh>

#include <darwin/platformrenderer.hh>

#ifndef MAC_OS_X_VERSION_10_12
#    define MAC_OS_X_VERSION_10_12 101200
#endif

#if __MAC_OS_X_VERSION_MIN_REQUIRED < MAC_OS_X_VERSION_10_12
#    define NSEventMaskAny NSAnyEventMask
#endif

namespace Motor { namespace Windowing {

Renderer::PlatformRenderer::PlatformRenderer()
{
    m_pool        = [[NSAutoreleasePool alloc] init];
    m_application = [NSApplication sharedApplication];

    NSMenu*     menu = [[NSMenu alloc] initWithTitle:@"motor"];
    NSMenuItem* mi   = [menu addItemWithTitle:@"Apple" action:Nil keyEquivalent:@""];
    NSMenu*     m    = [[NSMenu alloc] initWithTitle:@"Apple"];
    [menu setSubmenu:m forItem:mi];
    mi = [m addItemWithTitle:@"Quit" action:Nil keyEquivalent:@""];
    [mi setTarget:m_application];
    [mi setAction:@selector(stop:)];
    [NSApp performSelector:@selector(setAppleMenu:) withObject:m];
    [m_application setMainMenu:menu];
    [m_application finishLaunching];
}

Renderer::PlatformRenderer::~PlatformRenderer()
{
    [m_pool release];
}

void Renderer::PlatformRenderer::flush()
{
    [m_pool release];
    m_pool = [[NSAutoreleasePool alloc] init];
    while(NSEvent* event = [m_application nextEventMatchingMask:NSEventMaskAny
                                                      untilDate:nil
                                                         inMode:NSDefaultRunLoopMode
                                                        dequeue:YES])
    {
        [m_application sendEvent:event];
        [m_application updateWindows];
    }
}

Renderer::Renderer(minitl::Allocator& arena, weak< Resource::ResourceManager > manager)
    : IRenderer(arena, manager, Scheduler::MainThread)
    , m_platformRenderer(scoped< PlatformRenderer >::create(arena))
{
}

Renderer::~Renderer()
{
}

knl::uint2 Renderer::getScreenSize() const
{
    NSArray*  screens = [NSScreen screens];
    NSScreen* screen  = [screens objectAtIndex:0];
    NSRect    frame   = [screen visibleFrame];
    return knl::uint2 {(u32)frame.size.width, (u32)frame.size.height};
}

void Renderer::flush()
{
    IRenderer::flush();
    m_platformRenderer->flush();
}

bool Renderer::hasPlatformRenderer() const
{
    return true;
}

}}  // namespace Motor::Windowing
