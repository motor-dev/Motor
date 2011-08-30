/* BugEngine / Copyright (C) 2005-2009  screetch <screetch@gmail.com>
   see LICENSE for detail */

#include    <3d/stdafx.h>
#include    <3d/rendertarget/rendertarget.script.hh>

namespace BugEngine { namespace Graphics
{

RenderTarget::RenderTarget(u16 width, u16 height)
    :   dimensions(width, height)
{
}

RenderTarget::~RenderTarget()
{
}

RenderWindow::RenderWindow(u16 width, u16 height, istring title, bool fullscreen)
    :   RenderTarget(width, height)
    ,   title(title)
    ,   fullscreen(fullscreen)
{
}

RenderWindow::~RenderWindow()
{
}

}}