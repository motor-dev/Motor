/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#ifndef MOTOR_GL4_LOADERS_MESH_GLMESH_HH_
#define MOTOR_GL4_LOADERS_MESH_GLMESH_HH_
/**************************************************************************************************/
#include <motor/plugin.graphics.GL4/stdafx.h>
#include <motor/plugin.graphics.3d/renderer/igpuresource.hh>

namespace Motor { namespace OpenGL {

class GLRenderer;

class GLMesh : public IGPUResource
{
public:
    GLMesh(weak< const Resource::IDescription > meshDescription, weak< GLRenderer > renderer);
    ~GLMesh();

    virtual void load(weak< const Resource::IDescription > meshDescription) override;
    virtual void unload() override;
};

}}  // namespace Motor::OpenGL

/**************************************************************************************************/
#endif
