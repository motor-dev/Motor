/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */
#ifndef MOTOR_PLUGIN_SCRIPTING_PACKAGE_NODES_PACKAGE_HH
#define MOTOR_PLUGIN_SCRIPTING_PACKAGE_NODES_PACKAGE_HH

#include <motor/plugin.scripting.package/stdafx.h>

#include <motor/introspect/dbcontext.hh>
#include <motor/introspect/node/node.hh>
#include <motor/meta/value.hh>
#include <motor/minitl/hashmap.hh>
#include <motor/minitl/intrusive_list.hh>
#include <motor/minitl/vector.hh>
#include <motor/plugin/plugin.hh>

namespace Motor { namespace PackageBuilder { namespace Nodes {

class Package : public minitl::pointer
{
private:
    const ifilename                                     m_filename;
    Meta::AST::DbContext                                m_context;
    minitl::vector< Plugin::Plugin< minitl::pointer > > m_plugins;
    minitl::vector< ref< Meta::AST::Node > >            m_nodes;

public:
    Package(const ifilename& filename, const ref< Folder >& dataFolder);
    ~Package() override;

    void                   insertNode(istring name, const ref< Meta::AST::Node >& object);
    void                   removeNode(const ref< Meta::AST::Node >& object);
    ref< Meta::AST::Node > findByName(istring name) const;

    void loadPlugin(const inamespace& plugin, const inamespace& name);

    void createObjects(const weak< Resource::ResourceManager >&             manager,
                       minitl::vector< Plugin::Plugin< minitl::pointer > >& plugins,
                       minitl::vector< Meta::Value >&                       values);
    void diffFromPackage(const weak< Package >&                   previous,
                         const weak< Resource::ResourceManager >& manager);

    void resolve();

    const ifilename& filename() const;

    bool success() const;

    const Meta::AST::DbContext& context() const
    {
        return m_context;
    }

    Meta::AST::DbContext& context()
    {
        return m_context;
    }
};

}}}  // namespace Motor::PackageBuilder::Nodes

#endif
