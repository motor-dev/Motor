/* BugEngine / Copyright (C) 2005-2009  screetch <screetch@gmail.com>
   see LICENSE for detail */

#ifndef BE_RENDERNULL_LOADERS_NULLWINDOW_HH_
#define BE_RENDERNULL_LOADERS_NULLWINDOW_HH_
/*****************************************************************************/
#include    <graphics/renderer/irendertarget.hh>
#include    <graphics/renderer/irenderer.hh>


namespace BugEngine { namespace Graphics { namespace Null
{

class NullRenderer;

class NullWindow : public IRenderTarget
{
public:
    NullWindow(weak<const RenderWindow> resource, weak<NullRenderer> renderer);
    ~NullWindow();

private:
    void load(weak<const Resource> resource) override;
    void unload() override;

    void begin(ClearMode clear) const override;
    void end(PresentMode present) const override;

    void present() const;
};

}}}

/*****************************************************************************/
#endif
