/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <motor/plugin.graphics.GL4/stdafx.h>
#include <motor/plugin.graphics.3d/mesh/mesh.meta.hh>
#include <motor/plugin.graphics.GL4/glrenderer.hh>
#include <loaders/mesh/glmesh.hh>

namespace Motor { namespace OpenGL {

GLMesh::GLMesh(const weak< const Resource::IDescription >& meshDescription,
               const weak< GLRenderer >&                   renderer)
    : IGPUResource(meshDescription, renderer)
{
}

GLMesh::~GLMesh() = default;

void GLMesh::load(const weak< const Resource::IDescription >& /*meshDescription*/)
{
}

void GLMesh::unload()
{
}

}}  // namespace Motor::OpenGL
