/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#include <motor/plugin.graphics.GL4/stdafx.h>
#include <loaders/mesh/glmesh.hh>
#include <motor/plugin.graphics.3d/mesh/mesh.script.hh>
#include <motor/plugin.graphics.GL4/glrenderer.hh>

namespace Motor { namespace OpenGL {

GLMesh::GLMesh(weak< const Resource::Description > meshDescription, weak< GLRenderer > renderer)
    : IGPUResource(meshDescription, renderer)
{
}

GLMesh::~GLMesh()
{
}

void GLMesh::load(weak< const Resource::Description > /*meshDescription*/)
{
}

void GLMesh::unload()
{
}

}}  // namespace Motor::OpenGL
