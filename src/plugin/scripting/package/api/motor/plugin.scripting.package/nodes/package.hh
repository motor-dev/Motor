/* Motor <motor.devel@gmail.com>
   see LICENSE for detail */

#ifndef MOTOR_PACKAGE_NODES_PACKAGE_HH_
#define MOTOR_PACKAGE_NODES_PACKAGE_HH_
/**************************************************************************************************/
#include <motor/plugin.scripting.package/stdafx.h>

#include <motor/introspect/dbcontext.hh>
#include <motor/introspect/node/node.hh>
#include <motor/meta/value.hh>
#include <motor/minitl/hash_map.hh>
#include <motor/minitl/intrusive_list.hh>
#include <motor/minitl/vector.hh>
#include <motor/plugin/plugin.hh>

namespace Motor { namespace PackageBuilder { namespace Nodes {

class Package : public minitl::refcountable
{
private:
    const ifilename                           m_filename;
    Meta::AST::DbContext                      m_context;
    minitl::vector< Plugin::Plugin< void* > > m_plugins;
    minitl::vector< ref< Meta::AST::Node > >  m_nodes;
    minitl::vector< Meta::Value >             m_values;
    Meta::Value                               m_empty;

public:
    Package(const ifilename& filename, ref< Folder > dataFolder);
    ~Package();

    void                   insertNode(const istring name, ref< Meta::AST::Node > object);
    void                   removeNode(ref< Meta::AST::Node > object);
    ref< Meta::AST::Node > findByName(istring name) const;
    const Meta::Value&     getValue(weak< const Meta::AST::Node > object) const;

    void loadPlugin(inamespace plugin, inamespace name);

    void createObjects(weak< Resource::ResourceManager > manager);
    void deleteObjects(weak< Resource::ResourceManager > manager);
    void diffFromPackage(weak< Package > previous, weak< Resource::ResourceManager > manager);

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

/**************************************************************************************************/
#endif
