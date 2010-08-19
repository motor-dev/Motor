/* BugEngine / Copyright (C) 2005-2009  screetch <screetch@gmail.com>
   see LICENSE for detail */

#ifndef BE_OPENGL_RENDERER_HH_
#define BE_OPENGL_RENDERER_HH_
/*****************************************************************************/
#include    <system/filesystem.hh>

namespace BugEngine { namespace Graphics { namespace OpenGL
{

class Window;
class VertexBuffer;
class IndexBuffer;
class TextureBuffer;

class Renderer : public Windowing::Renderer
{
    friend class Window;
    friend class VertexBuffer;
    friend class IndexBuffer;
    friend class TextureBuffer;
    friend class ShaderPipeline;
    friend class TexturePipeline;
private:
#   ifdef BE_PLATFORM_WIN32
    HGLRC                       m_glContext;
#   else
    GLXContext                  m_glContext;
#   endif
    weak<const FileSystem>      m_filesystem;
public:
    Renderer(weak<const FileSystem> filesystem);
    ~Renderer();

    ref<Graphics::IRenderTarget>    createRenderWindow(WindowFlags flags) override;
    ref<Graphics::IRenderTarget>    createRenderBuffer(TextureFlags flags) override;
    ref<Graphics::IRenderTarget>    createMultipleRenderBuffer(TextureFlags flags, size_t count) override;
    ref<GpuBuffer>                  createVertexBuffer(u32 vertexCount, VertexUsage usage, VertexBufferFlags flags) const override;
    ref<GpuBuffer>                  createIndexBuffer(u32 vertexCount, IndexUsage usage, IndexBufferFlags flags) const override;

    u32                             getMaxSimultaneousRenderTargets() const override { return 1; }
    bool                            multithreaded() const override {return true; }

    void                            flush() override;

    weak<const FileSystem>          filesystem() const  { return m_filesystem; }
private:
    void                            attachWindow(Window* w);
    void                            drawBatch(const Batch& b);

public:
    void* operator new(size_t size)                  { return ::operator new(size); }
    void* operator new(size_t size, void* where)     { return ::operator new(size, where); }
public:
    void  operator delete(void* memory)              { return ::operator delete(memory); }
    void  operator delete(void* memory, void* where) { return ::operator delete(memory, where); }
};

}}}

/*****************************************************************************/
#endif
