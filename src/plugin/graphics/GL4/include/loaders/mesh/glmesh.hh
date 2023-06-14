/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#ifndef MOTOR_PLUGIN_GRAPHICS_GL4_LOADERS_MESH_GLMESH_HH
#define MOTOR_PLUGIN_GRAPHICS_GL4_LOADERS_MESH_GLMESH_HH

#include <motor/plugin.graphics.GL4/stdafx.h>
#include <motor/plugin.graphics.3d/renderer/igpuresource.hh>

namespace Motor { namespace OpenGL {

class GLRenderer;

class GLMesh : public IGPUResource
{
public:
    GLMesh(const weak< const Resource::IDescription >& meshDescription,
           const weak< GLRenderer >&                   renderer);
    ~GLMesh() override;

    void load(const weak< const Resource::IDescription >& meshDescription) override;
    void unload() override;
};

}}  // namespace Motor::OpenGL

#endif
